.. autoclass:: {{ objname }}
   
    {% block methods %}
    {% if methods %}
    .. rubric:: Methods
        
        {% for item in methods %}
            {%- if item != '__init__' %}
            ~{{ objname }}.{{ item }}
            {%- endif -%}
        {%- endfor %}
        {% endif %}
        {% endblock %}
   
