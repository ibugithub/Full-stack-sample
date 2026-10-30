from django import template

register = template.Library()


@register.inclusion_tag('admin/includes/list_filters.html')
def record_filters(cl):
    groups = []
    selected = []
    for spec in cl.filter_specs:
        choices = list(spec.choices(cl))
        clear_url = cl.get_query_string(remove=spec.expected_parameters())
        active = [choice for choice in choices if choice.get('selected')] if choices and not choices[0].get('selected') else []
        if choices and not choices[0].get('selected') and not active:
            active = [{'selected': True, 'query_string': cl.get_query_string(), 'display': 'Custom'}]
        for choice in active:
            selected.append({'title': spec.title, 'display': choice['display'], 'clear_url': clear_url})
        visible = choices[:4]
        remaining = choices[4:]
        # Keep a chosen value visible even when it lies beyond the quick choices.
        for choice in active:
            if choice not in visible:
                visible.append(choice)
                if choice in remaining:
                    remaining.remove(choice)
        groups.append({'title': spec.title, 'visible': visible, 'remaining': remaining, 'choices': choices})
    return {
        'quick_filters': groups[:1], 'more_filters': groups[1:],
        'selected_filters': selected, 'clear_all_url': cl.clear_all_filters_qs,
    }
