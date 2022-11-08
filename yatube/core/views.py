from http import HTTPStatus

from django.shortcuts import render


def page_not_found(request, exception):
    template = 'core/404.html'
    return render(
        request,
        template,
        {
            'path': request.path,
        },
        status=HTTPStatus.NOT_FOUND
    )


def csrf_failure(request, reason=''):
    template = 'core/403csrf.html'
    return render(request, template, HTTPStatus.FORBIDDEN)


def internal_error(request, *args, **kwargs):
    template = 'core/500.html'
    return render(request, template, HTTPStatus.INTERNAL_SERVER_ERROR)
