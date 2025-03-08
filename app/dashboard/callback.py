def dashboard_callback(request, context):
    context.update({
        "test": "test"
    })
    return context
