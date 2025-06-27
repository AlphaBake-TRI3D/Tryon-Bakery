from django.shortcuts import render
import json

def compare(request):

    # models_list = ['alphabake150-fast', 'alphabake150-quality', 'fashnai-quality']
    comparision_data = json.load(open('samples/44_pairs_data-comparision.json'))

    # get the model list from the comparision data
    models_list = list(comparision_data[list(comparision_data.keys())[1]].keys())
    print(models_list,comparision_data[list(comparision_data.keys())[1]])
    models_list.remove('name')
    models_list.remove('human')
    models_list.remove('garment')

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