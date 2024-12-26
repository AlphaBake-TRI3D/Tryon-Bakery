from django.shortcuts import render, get_object_or_404
from .models import TryonBatch, Tryon

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
