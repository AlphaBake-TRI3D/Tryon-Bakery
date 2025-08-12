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
    # remove the models that have _realism in the name
    models_list = [model for model in models_list if '_realism' not in model.lower()]

    comparisons = []
    for item_value in comparision_data.values():
        model_images = []
        images_alone = []
        for model in models_list:
            model_images.append(
                {
                    'url': item_value.get(model),
                    'garment_realism': str(item_value.get(model + '_garment_realism') if model + '_garment_realism' in item_value else None),
                    'body_type_realism': str(item_value.get(model + '_body_type_realism') if model + '_body_type_realism' in item_value else None),
                    'overall_realism': str(item_value.get(model + '_overall_realism') if model + '_overall_realism' in item_value else None),
                    'face_realism': str(item_value.get(model + '_face_realism') if model + '_face_realism' in item_value else None),
                    'model_name': model
                }
            )
            images_alone.append(item_value.get(model))
        
        comparisons.append({
            'name': item_value['name'],
            'human': item_value['human'],
            'garment': item_value['garment'],
            'model_images': model_images,
            'images_alone': images_alone
        })

    context = {
        'comparisons': comparisons,
        'models_list': models_list
    }
    return render(request, 'main/compare.html', context)


def compareG(request):

    # models_list = ['alphabake150-fast', 'alphabake150-quality', 'fashnai-quality']
    comparision_data = json.load(open('samples/google-comparision.json'))

    # get the model list from the comparision data
    models_list = list(comparision_data[list(comparision_data.keys())[5]].keys())
    print(models_list,comparision_data[list(comparision_data.keys())[5]])
    models_list.remove('name')
    models_list.remove('human')
    models_list.remove('garment')
    # move google-1.0 to the first position
    models_list.remove('google-shopping-20250708')
    models_list.insert(1, 'google-shopping-20250708')
    # remove the models that have _realism in the name
    models_list = [model for model in models_list if '_realism' not in model.lower()]

    comparisons = []
    for item_value in comparision_data.values():
        model_images = []
        images_alone = []
        for model in models_list:
            model_images.append(
                {
                    'url': item_value.get(model),
                    'garment_realism': str(item_value.get(model + '_garment_realism') if model + '_garment_realism' in item_value else None),
                    'body_type_realism': str(item_value.get(model + '_body_type_realism') if model + '_body_type_realism' in item_value else None),
                    'overall_realism': str(item_value.get(model + '_overall_realism') if model + '_overall_realism' in item_value else None),
                    'face_realism': str(item_value.get(model + '_face_realism') if model + '_face_realism' in item_value else None),
                    'model_name': model
                }
            )
            images_alone.append(item_value.get(model))
        
        comparisons.append({
            'name': item_value['name'],
            'human': item_value['human'],
            'garment': item_value['garment'],
            'model_images': model_images,
            'images_alone': images_alone
        })

    context = {
        'comparisons': comparisons,
        'models_list': models_list,
        'is_google': True
    }
    return render(request, 'main/compare.html', context)


def compareM(request):

    # models_list = ['alphabake150-fast', 'alphabake150-quality', 'fashnai-quality']
    comparision_data = json.load(open('samples/compareM-comparision.json'))

    # get the model list from the comparision data
    models_list = list(comparision_data[list(comparision_data.keys())[5]].keys())
    print(models_list,comparision_data[list(comparision_data.keys())[5]])
    models_list.remove('name')
    models_list.remove('human')
    models_list.remove('garment')
    # remove the models that have _realism in the name
    models_list = [model for model in models_list if '_realism' not in model.lower()]

    comparisons = []
    for item_value in comparision_data.values():
        model_images = []
        images_alone = []
        for model in models_list:
            model_images.append(
                {
                    'url': item_value.get(model),
                    'garment_realism': str(item_value.get(model + '_garment_realism') if model + '_garment_realism' in item_value else None),
                    'body_type_realism': str(item_value.get(model + '_body_type_realism') if model + '_body_type_realism' in item_value else None),
                    'overall_realism': str(item_value.get(model + '_overall_realism') if model + '_overall_realism' in item_value else None),
                    'face_realism': str(item_value.get(model + '_face_realism') if model + '_face_realism' in item_value else None),
                    'model_name': model
                }
            )
            images_alone.append(item_value.get(model))
        
        comparisons.append({
            'name': item_value['name'],
            'human': item_value['human'],
            'garment': item_value['garment'],
            'model_images': model_images,
            'images_alone': images_alone
        })

    context = {
        'comparisons': comparisons,
        'models_list': models_list,
    }
    return render(request, 'main/compare.html', context)

def compare200(request):

    # models_list = ['alphabake150-fast', 'alphabake150-quality', 'fashnai-quality']
    comparision_data = json.load(open('samples/200pairs-v3-comparision.json'))

    # get the model list from the comparision data
    models_list = list(comparision_data[list(comparision_data.keys())[5]].keys())
    print(models_list,comparision_data[list(comparision_data.keys())[5]])
    models_list.remove('name')
    models_list.remove('human')
    models_list.remove('garment')
    # remove the models that have _realism in the name
    models_list = [model for model in models_list if '_realism' not in model.lower()]
    models_list.remove('garment_type')
    comparisons = []
    for item_value in comparision_data.values():
        model_images = []
        images_alone = []
        for model in models_list:
            model_images.append(
                {
                    'url': item_value.get(model),
                    'garment_realism': str(item_value.get(model + '_garment_realism') if model + '_garment_realism' in item_value else None),
                    'body_type_realism': str(item_value.get(model + '_body_type_realism') if model + '_body_type_realism' in item_value else None),
                    'overall_realism': str(item_value.get(model + '_overall_realism') if model + '_overall_realism' in item_value else None),
                    'face_realism': str(item_value.get(model + '_face_realism') if model + '_face_realism' in item_value else None),
                    'model_name': model
                }
            )
            images_alone.append(item_value.get(model))
        
        comparisons.append({
            'name': item_value['name'],
            'human': item_value['human'],
            'garment': item_value['garment'],
            'model_images': model_images,
            'images_alone': images_alone,
            'garment_type': item_value['garment_type']
        })

    context = {
        'comparisons': comparisons,
        'models_list': models_list,
    }
    return render(request, 'main/compare.html', context)