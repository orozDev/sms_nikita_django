from django.utils import timezone


class LastUserActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user

        if user.is_authenticated:
            user.last_activity = timezone.now()
            user.save()

        response = self.get_response(request)

        return response