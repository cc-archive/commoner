from django.shortcuts import render_to_response

def content_detail(request, content_id):

    return render_to_response('content/detail.html',
                              {'content':None})
