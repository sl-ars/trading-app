def user_context_processor(request):
    """
    Passes user roles to templates so they can be used for RBAC.
    """
    return {
        'user_role': request.user.role if request.user.is_authenticated else None
    }