from django.shortcuts import render
import json

def compare(request):

    models_list = ['alphabake150-fast', 'alphabake150-quality', 'fashnai-quality']
    comparision_data = json.load(open('samples/5pairs-v-small-comparision.json'))

    comparisons = []
    for item_value in comparision_data.values():
        model_images = []
        for model in models_list:
            model_images.append(item_value.get(model))
        
        comparisons.append({
            'name': item_value['name'],
            'human': item_value['human'],
            'garment': item_value['garment'],
            'model_images': model_images
        })

    context = {
        'comparisons': comparisons,
        'models_list': models_list
    }
    return render(request, 'main/compare.html', context)