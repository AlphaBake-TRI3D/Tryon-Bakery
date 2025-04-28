from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import uuid
from .models import TryonBatch, Tryon, PasswordResetToken, InputSet, ModelVersion, RankedPair
import boto3
from PIL import Image
import io
from tryon_menu.aws_constants import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
    AWS_S3_REGION_NAME
)
from django.core.paginator import Paginator
from io import BytesIO
from django.urls import reverse

def index_view(request):
    return redirect('modelversion_list')

@login_required
def comparison_view(request, batch_id):
    if not batch_id:
        return redirect('batch_selection')
    
    batch = get_object_or_404(TryonBatch, id=batch_id)
    
    # Get all unranked pairs for this batch
    ranked_pairs = RankedPair.objects.filter(tryon_batch=batch, user=request.user).values_list('winner_tryon', 'loser_tryon')
    
    # Get all tryons in this batch with related data
    tryons = list(batch.tryons.all().select_related(
        'model_version',
        'model_version__model',
        'input_set'
    ))
    
    # Find an unranked pair
    unranked_pair = None
    for i in range(len(tryons)):
        for j in range(i + 1, len(tryons)):
            if (tryons[i].id, tryons[j].id) not in ranked_pairs and (tryons[j].id, tryons[i].id) not in ranked_pairs:
                unranked_pair = (tryons[i], tryons[j])
                break
        if unranked_pair:
            break
    
    context = {
        'batch': batch,
        'unranked_pair': unranked_pair,
    }
    
    return render(request, 'main/comparison_view.html', context)

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Try to authenticate with username
        user = authenticate(username=username, password=password)
        
        # If failed, try with email
        if not user and '@' in username:
            try:
                user_obj = User.objects.get(email=username)
                user = authenticate(username=user_obj.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user:
            login(request, user)
            return redirect('index')
        else:
            return render(request, 'main/auth/login.html', {'error': 'Invalid credentials'})
    
    return render(request, 'main/auth/login.html')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            return render(request, 'main/auth/signup.html', {'error': 'Passwords do not match'})
        
        if User.objects.filter(username=username).exists():
            return render(request, 'main/auth/signup.html', {'error': 'Username already exists'})
        
        if User.objects.filter(email=email).exists():
            return render(request, 'main/auth/signup.html', {'error': 'Email already exists'})
        
        user = User.objects.create_user(username=username, email=email, password=password)
        login(request, user)
        return redirect('index')
    
    return render(request, 'main/auth/signup.html')

def logout_view(request):
    logout(request)
    return redirect('login')

def password_reset_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            token = str(uuid.uuid4())
            
            # Save the token
            PasswordResetToken.objects.create(user=user, token=token)
            
            # Send reset email
            reset_link = f"{request.scheme}://{request.get_host()}/reset-password/{token}"
            send_mail(
                'Password Reset Request',
                f'Click the following link to reset your password: {reset_link}',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            return render(request, 'main/auth/password_reset.html', {
                'success': 'Password reset instructions have been sent to your email'
            })
            
        except User.DoesNotExist:
            return render(request, 'main/auth/password_reset.html', {
                'error': 'No user found with this email address'
            })
    
    return render(request, 'main/auth/password_reset.html')

def password_reset_confirm_view(request, token):
    try:
        reset_token = PasswordResetToken.objects.get(token=token, used=False)
        
        if request.method == 'POST':
            password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            
            if password != confirm_password:
                return render(request, 'main/auth/password_reset_confirm.html', {
                    'error': 'Passwords do not match',
                    'token': token
                })
            
            user = reset_token.user
            user.set_password(password)
            user.save()
            
            reset_token.used = True
            reset_token.save()
            
            return redirect('login')
        
        return render(request, 'main/auth/password_reset_confirm.html', {'token': token})
        
    except PasswordResetToken.DoesNotExist:
        return redirect('password_reset')

def create_thumbnail(image_file, max_size=(600, 600)):
    image = Image.open(image_file)
    image.thumbnail(max_size)
    thumbnail_io = io.BytesIO()
    image.save(thumbnail_io, format=image.format)
    thumbnail_io.seek(0)
    return thumbnail_io

@login_required
def upload_images(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        garment_image = request.FILES.get('garment_image')
        model_image = request.FILES.get('model_image')
        prompt = request.POST.get('prompt', '')  # Get prompt for video mode

        if name and model_image:
            try:
                # Initialize S3 client
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    region_name=AWS_S3_REGION_NAME
                )

                # Create thumbnails
                model_image.seek(0)
                model_thumbnail = create_thumbnail(model_image)

                # Reset file pointers
                model_image.seek(0)

                # Generate unique filenames
                timestamp = uuid.uuid4().hex[:8]
                model_ext = model_image.name.split('.')[-1]

                # Create S3 keys
                model_key = f'models/{timestamp}_{name}_model.{model_ext}'
                model_thumb_key = f'thumbnails/models/{timestamp}_{name}_model_thumb.{model_ext}'

                # Upload files to S3
                s3_client.upload_fileobj(model_image, AWS_STORAGE_BUCKET_NAME, model_key)
                s3_client.upload_fileobj(model_thumbnail, AWS_STORAGE_BUCKET_NAME, model_thumb_key)

                # Create InputSet with S3 keys
                input_set = InputSet.objects.create(
                    name=name,
                    model_key=model_key,
                    model_thumb_key=model_thumb_key,
                    created_by=request.user,
                    mode='video' if prompt else 'image',  # Determine mode based on prompt
                    prompt=prompt
                )

                return redirect('inputset_detail', inputset_id=input_set.id)
            except Exception as e:
                return render(request, 'main/upload_images.html', {'error': str(e)})

    return render(request, 'main/upload_images.html')

@login_required
def inputset_list(request):
    inputsets = InputSet.objects.all().order_by('-created_at')
    return render(request, 'main/inputset_list.html', {'inputsets': inputsets})

@login_required
def inputset_detail(request, inputset_id):
    inputset = get_object_or_404(InputSet, id=inputset_id)
    return render(request, 'main/inputset_detail.html', {'inputset': inputset})

@login_required
def create_tryonbatch_step1(request):
    mode = request.GET.get('mode', 'image')  # Default to image if mode is not specified
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        input_set_id = request.POST.get('input_set')
        model_version_ids = request.POST.getlist('model_versions')
        
        if name and input_set_id and model_version_ids:
            # Store the selection in session for step 2
            request.session['tryonbatch_data'] = {
                'name': name,
                'description': description,
                'input_set_id': input_set_id,
                'model_version_ids': model_version_ids,
                'mode': mode  # Use mode from URL
            }
            return redirect(f"{reverse('create_tryonbatch_step2')}?mode={mode}")  # Append mode manually
    
    input_sets = InputSet.objects.filter(mode=mode).order_by('-created_at')  # Filter by mode
    model_versions = ModelVersion.objects.filter(model__model_type=mode).select_related('model').order_by('-created_at')  # Filter by mode
    
    return render(request, 'main/tryonbatch_create_step1.html', {
        'input_sets': input_sets,
        'model_versions': model_versions
    })

@login_required
def create_tryonbatch_step2(request):
    from main.utils import generate_tryon_via_api, generate_video_via_api
    # Get data from session
    tryonbatch_data = request.session.get('tryonbatch_data')
    if not tryonbatch_data:
        return redirect(f"{reverse('create_tryonbatch_step1')}?mode={request.GET.get('mode', 'image')}")  # Append mode manually
    
    if request.method == 'POST':
        try:
            # Create the batch
            batch = TryonBatch.objects.create(
                name=tryonbatch_data['name'],
                description=tryonbatch_data['description']
            )
            
            input_set = InputSet.objects.get(id=tryonbatch_data['input_set_id'])
            model_versions = ModelVersion.objects.filter(id__in=tryonbatch_data['model_version_ids'])
            
            # Initialize S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                region_name=AWS_S3_REGION_NAME
            )
            
            # Process each model version
            for model_version in model_versions:
                if model_version.is_api_implemented:
                    if tryonbatch_data['mode'] == 'video':
                        # Use API to generate video
                        try:
                            video_key, time_taken = generate_video_via_api(input_set, model_version, s3_client)
                            
                            # Create Tryon object with video results
                            tryon = Tryon.objects.create(
                                input_set=input_set,
                                model_version=model_version,
                                image_key=video_key,  # Use video key
                                thumb_key=None,  # No thumbnail for video
                                is_generated_by_api=True,
                                time_taken=time_taken,
                                resolution=None,
                                price_per_inference=model_version.price_per_inference,
                                notes="",  # Use the captured notes
                                mode=tryonbatch_data['mode']  # Set mode
                            )
                            batch.tryons.add(tryon)
                        except Exception as e:
                            # Log the error but continue with other models
                            print(f"API error for {model_version}: {str(e)}")
                            continue
                    else:
                        # Use API to generate tryon
                        try:
                            image_key, thumb_key, resolution, time_taken = generate_tryon_via_api(input_set, model_version, s3_client)
                            
                            # Create Tryon object with API results
                            tryon = Tryon.objects.create(
                                input_set=input_set,
                                model_version=model_version,
                                image_key=image_key,
                                thumb_key=thumb_key,
                                is_generated_by_api=True,
                                time_taken=time_taken,
                                resolution=resolution,
                                price_per_inference=model_version.price_per_inference,
                                notes="",  # Empty string for text field
                                mode=tryonbatch_data['mode']  # Set mode
                            )
                            batch.tryons.add(tryon)
                        except Exception as e:
                            # Log the error but continue with other models
                            print(f"API error for {model_version}: {str(e)}")
                            continue
                else:
                    # Handle manual upload
                    file_key = f'model_version_{model_version.id}'
                    if file_key in request.FILES:
                        uploaded_file = request.FILES[file_key]
                        notes = request.POST.get(f'notes_{model_version.id}', '')  # Get notes from form
                        
                        # Generate unique filenames
                        timestamp = uuid.uuid4().hex[:8]
                        
                        if tryonbatch_data['mode'] == 'video':
                            # Handle video file
                            video_key = f'tryons/{timestamp}_{batch.name}_{model_version.id}.mp4'
                            s3_client.upload_fileobj(uploaded_file, AWS_STORAGE_BUCKET_NAME, video_key)
                            
                            # Create Tryon object
                            tryon = Tryon.objects.create(
                                input_set=input_set,
                                model_version=model_version,
                                image_key=video_key,  # Use video key
                                thumb_key=None,  # No thumbnail for video
                                is_generated_by_api=False,
                                time_taken=None,
                                resolution=None,
                                price_per_inference=model_version.price_per_inference,
                                notes=notes,  # Use the captured notes
                                mode=tryonbatch_data['mode']  # Set mode
                            )
                            batch.tryons.add(tryon)
                        else:
                            # Handle image file
                            uploaded_file.seek(0)
                            with Image.open(uploaded_file) as img:
                                # Create thumbnail
                                thumbnail = img.copy()
                                thumbnail.thumbnail((600, 600))
                                thumb_buffer = BytesIO()
                                thumbnail.save(thumb_buffer, format='JPEG')
                                thumb_buffer.seek(0)
                                
                                # Get resolution
                                width, height = img.size
                                resolution = f"{width}x{height}"
                            
                            # Reset file pointer
                            uploaded_file.seek(0)
                            
                            # Generate unique filenames
                            timestamp = uuid.uuid4().hex[:8]
                            image_ext = uploaded_file.name.split('.')[-1]
                            
                            # Create S3 keys
                            image_key = f'tryons/{timestamp}_{batch.name}_{model_version.id}.{image_ext}'
                            thumb_key = f'thumbnails/tryons/{timestamp}_{batch.name}_{model_version.id}_thumb.{image_ext}'
                            
                            # Upload to S3
                            s3_client.upload_fileobj(uploaded_file, AWS_STORAGE_BUCKET_NAME, image_key)
                            s3_client.upload_fileobj(thumb_buffer, AWS_STORAGE_BUCKET_NAME, thumb_key)
                            
                            # Create Tryon object
                            tryon = Tryon.objects.create(
                                input_set=input_set,
                                model_version=model_version,
                                image_key=image_key,
                                thumb_key=thumb_key,
                                is_generated_by_api=False,
                                time_taken=None,
                                resolution=resolution,
                                price_per_inference=model_version.price_per_inference,
                                notes=notes,  # Use the captured notes
                                mode=tryonbatch_data['mode']  # Set mode
                            )
                            batch.tryons.add(tryon)
            
            # Clear session data
            del request.session['tryonbatch_data']
            return redirect('tryonbatch_detail', batch_id=batch.id)
            
        except Exception as e:
            return render(request, 'main/tryonbatch_create_step2.html', {
                'error': str(e),
                'input_set': InputSet.objects.get(id=tryonbatch_data['input_set_id']),
                'model_versions': ModelVersion.objects.filter(id__in=tryonbatch_data['model_version_ids'])
            })
    
    return render(request, 'main/tryonbatch_create_step2.html', {
        'input_set': InputSet.objects.get(id=tryonbatch_data['input_set_id']),
        'model_versions': ModelVersion.objects.filter(id__in=tryonbatch_data['model_version_ids'])
    })

def tryonbatch_detail(request, batch_id):
    batch = get_object_or_404(TryonBatch, id=batch_id)
    tryons = batch.tryons.all().select_related('model_version', 'model_version__model', 'input_set')
    
    return render(request, 'main/tryonbatch_detail.html', {
        'batch': batch,
        'tryons': tryons,
        'input_set': tryons.first().input_set if tryons.exists() else None
    })

def modelversion_list(request):
    model_versions = ModelVersion.objects.all().select_related('model', 'model__organization').order_by('-elo_rating', '-created_at')
    return render(request, 'main/modelversion_list.html', {'model_versions': model_versions})

def modelversion_detail(request, modelversion_id):
    model_version = get_object_or_404(ModelVersion, id=modelversion_id)
    if request.method == 'POST' and request.user.is_staff:
        # Handle form submission for admin editing
        model_version.version = request.POST.get('version')
        model_version.resolution = request.POST.get('resolution')
        model_version.description = request.POST.get('description')
        
        # Update model URL
        model = model_version.model
        model.url = request.POST.get('model_url', '')
        model.save()
        
        model_version.save()
        return redirect('modelversion_detail', modelversion_id=modelversion_id)
    
    return render(request, 'main/modelversion_detail.html', {
        'model_version': model_version,
        'can_edit': request.user.is_staff
    })

@login_required
def rank_models(request):
    batch_id = request.GET.get('batch_id')
    if batch_id:
        batch = get_object_or_404(TryonBatch, id=batch_id)
        tryons = batch.tryons.all()
        
        # Get already ranked pairs for this user and batch
        ranked_pairs = RankedPair.objects.filter(
            user=request.user,
            tryon_batch=batch
        ).values_list('winner_tryon_id', 'loser_tryon_id')
        
        # Create a set of ranked pairs for quick lookup
        ranked_set = {(w, l) for w, l in ranked_pairs} | {(l, w) for w, l in ranked_pairs}
        
        # Find unranked pairs
        unranked_pairs = []
        tryon_list = list(tryons)
        for i, tryon1 in enumerate(tryon_list):
            for tryon2 in tryon_list[i+1:]:
                if (tryon1.id, tryon2.id) not in ranked_set:
                    unranked_pairs.append((tryon1, tryon2))
                    break  # Only get one unranked pair per tryon
            if unranked_pairs:
                break  # Stop after finding first unranked pair
        
        context = {
            'batch': batch,
            'unranked_pair': unranked_pairs[0] if unranked_pairs else None,
        }
    else:
        # Show list of batches that have items to rank
        batches = TryonBatch.objects.all().order_by('-created_at')
        context = {'batches': batches}
    
    return render(request, 'main/rank_models.html', context)

@login_required
def submit_ranking(request):
    if request.method == 'POST':
        winner_id = request.POST.get('winner_id')
        loser_id = request.POST.get('loser_id')
        batch_id = request.POST.get('batch_id')
        notes = request.POST.get('notes', '')
        
        winner = get_object_or_404(Tryon, id=winner_id)
        loser = get_object_or_404(Tryon, id=loser_id)
        batch = get_object_or_404(TryonBatch, id=batch_id)
        
        RankedPair.objects.create(
            user=request.user,
            tryon_batch=batch,
            winner_tryon=winner,
            loser_tryon=loser,
            notes=notes
        )
        
        return redirect('comparison_view', batch_id=batch_id)
    return redirect('batch_selection')

@login_required
def my_rankings(request):
    # Get the tab from query parameters, default to 'my'
    active_tab = request.GET.get('tab', 'my')
    
    # Base query with all necessary related fields
    base_query = RankedPair.objects.select_related(
        'winner_tryon__model_version',
        'winner_tryon__model_version__model',
        'loser_tryon__model_version',
        'loser_tryon__model_version__model',
        'tryon_batch',
        'user'
    ).order_by('-created_at')
    
    # Filter based on active tab
    if active_tab == 'my':
        rankings = base_query.filter(user=request.user)
    else:  # 'all' tab
        rankings = base_query
    
    # Pagination
    paginator = Paginator(rankings, 20)  # Show 20 rankings per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'active_tab': active_tab,
    }
    
    return render(request, 'main/my_rankings.html', context)

@login_required
def delete_ranking(request, ranking_id):
    if request.method == 'POST':
        ranking = get_object_or_404(RankedPair, id=ranking_id, user=request.user)
        
        # Get the model versions
        winner_model = ranking.winner_tryon.model_version
        loser_model = ranking.loser_tryon.model_version
        
        # Reverse the ELO changes if they exist
        if ranking.winner_rating_before is not None and ranking.loser_rating_before is not None:
            # Restore the original ratings
            winner_model.elo_rating = ranking.winner_rating_before
            loser_model.elo_rating = ranking.loser_rating_before
            
            # Save the model versions with their restored ratings
            winner_model.save()
            loser_model.save()
        
        # Delete the ranking
        ranking.delete()
        
    return redirect('my_rankings')

@login_required
def batch_selection(request):
    batches = TryonBatch.objects.all().order_by('-created_at')
    return render(request, 'main/batch_selection.html', {'batches': batches})

@login_required
def tryonbatch_list(request):
    batches = TryonBatch.objects.all().order_by('-created_at')
    return render(request, 'main/tryonbatch_list.html', {'batches': batches})
