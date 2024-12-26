from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import uuid
from .models import TryonBatch, Tryon, PasswordResetToken, InputSet, ModelVersion
import boto3
from PIL import Image
import io
from tryon_menu.aws_constants import (
    AWS_ACCESS_KEY_ID,
    AWS_SECRET_ACCESS_KEY,
    AWS_STORAGE_BUCKET_NAME,
    AWS_S3_REGION_NAME
)

def index_view(request):
    batches = TryonBatch.objects.all().order_by('-created_at')
    return render(request, 'main/index.html', {'batches': batches})

def comparison_view(request, batch_id=None):
    # Get the latest batch if no batch_id is provided
    if batch_id is None:
        batch = TryonBatch.objects.latest('created_at')
    else:
        batch = get_object_or_404(TryonBatch, id=batch_id)
    
    # Get all tryons in this batch
    tryons = batch.tryons.all().select_related('model_version', 'model_version__model', 'input_set')
    
    # Prepare data for the template
    context = {
        'batch': batch,
        'tryons': tryons,
        'input_set': tryons.first().input_set if tryons.exists() else None,
    }
    
    return render(request, 'main/comparison.html', context)

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

        if name and garment_image and model_image:
            try:
                # Initialize S3 client
                s3_client = boto3.client(
                    's3',
                    aws_access_key_id=AWS_ACCESS_KEY_ID,
                    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                    region_name=AWS_S3_REGION_NAME
                )

                # Create thumbnails
                garment_image.seek(0)
                model_image.seek(0)
                garment_thumbnail = create_thumbnail(garment_image)
                model_thumbnail = create_thumbnail(model_image)

                # Reset file pointers
                garment_image.seek(0)
                model_image.seek(0)

                # Generate unique filenames
                timestamp = uuid.uuid4().hex[:8]
                garment_ext = garment_image.name.split('.')[-1]
                model_ext = model_image.name.split('.')[-1]
                
                # Create S3 keys
                garment_key = f'garments/{timestamp}_{name}_garment.{garment_ext}'
                model_key = f'models/{timestamp}_{name}_model.{model_ext}'
                garment_thumb_key = f'thumbnails/garments/{timestamp}_{name}_garment_thumb.{garment_ext}'
                model_thumb_key = f'thumbnails/models/{timestamp}_{name}_model_thumb.{model_ext}'

                # Upload files to S3
                s3_client.upload_fileobj(garment_image, AWS_STORAGE_BUCKET_NAME, garment_key)
                s3_client.upload_fileobj(model_image, AWS_STORAGE_BUCKET_NAME, model_key)
                s3_client.upload_fileobj(garment_thumbnail, AWS_STORAGE_BUCKET_NAME, garment_thumb_key)
                s3_client.upload_fileobj(model_thumbnail, AWS_STORAGE_BUCKET_NAME, model_thumb_key)

                # Create InputSet with S3 keys
                input_set = InputSet.objects.create(
                    name=name,
                    garment_key=garment_key,
                    model_key=model_key,
                    garment_thumb_key=garment_thumb_key,
                    model_thumb_key=model_thumb_key,
                    created_by=request.user
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
                'model_version_ids': model_version_ids
            }
            return redirect('create_tryonbatch_step2')
    
    input_sets = InputSet.objects.all().order_by('-created_at')
    model_versions = ModelVersion.objects.all().select_related('model').order_by('-created_at')
    
    return render(request, 'main/tryonbatch_create_step1.html', {
        'input_sets': input_sets,
        'model_versions': model_versions
    })

@login_required
def create_tryonbatch_step2(request):
    # Get data from session
    tryonbatch_data = request.session.get('tryonbatch_data')
    if not tryonbatch_data:
        return redirect('create_tryonbatch_step1')
    
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
            
            # Process each tryon image
            for model_version in model_versions:
                image_key = f'model_version_{model_version.id}'
                if image_key in request.FILES:
                    image = request.FILES[image_key]
                    notes = request.POST.get(f'notes_{model_version.id}', '')
                    
                    # Create thumbnail
                    image.seek(0)
                    thumbnail = create_thumbnail(image)
                    image.seek(0)
                    
                    # Generate unique filenames
                    timestamp = uuid.uuid4().hex[:8]
                    image_ext = image.name.split('.')[-1]
                    
                    # Create S3 keys
                    image_key = f'tryons/{timestamp}_{batch.name}_{model_version.id}.{image_ext}'
                    thumb_key = f'thumbnails/tryons/{timestamp}_{batch.name}_{model_version.id}_thumb.{image_ext}'
                    
                    # Upload to S3
                    s3_client.upload_fileobj(image, AWS_STORAGE_BUCKET_NAME, image_key)
                    s3_client.upload_fileobj(thumbnail, AWS_STORAGE_BUCKET_NAME, thumb_key)
                    
                    # Create Tryon object
                    tryon = Tryon.objects.create(
                        input_set=input_set,
                        model_version=model_version,
                        image_key=image_key,
                        thumb_key=thumb_key,
                        notes={'user_notes': notes}
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

@login_required
def tryonbatch_detail(request, batch_id):
    batch = get_object_or_404(TryonBatch, id=batch_id)
    tryons = batch.tryons.all().select_related('model_version', 'model_version__model', 'input_set')
    
    return render(request, 'main/tryonbatch_detail.html', {
        'batch': batch,
        'tryons': tryons,
        'input_set': tryons.first().input_set if tryons.exists() else None
    })
