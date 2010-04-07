print "Hello World";

{% for rate in rates_for_table %}
rate(
  {% for group in rate.group_definitions %}
  group{{ forloop.counter }} = 
"""
{{ group }}""",{% endfor %}
  kf = Arrhenius(A=({{rate.A}},"cm3/s"), n={{rate.n}}, alpha={{rate.alpha}}, E0=({{rate.E0}},"kcal/mol")),
  rank = {{ rate.rank }},
  old_id = "{{ rate.id }}",
  short_comment = "{{ rate.comment }}",
  long_comment = 
"""
{{ rate.long_comment }}"""
  
)
{% endfor %}