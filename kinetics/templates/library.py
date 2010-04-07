# encoding: utf-8
header = """
{{family.name}}

{{family.reaction|safe }}

{% if family.reverse %}
Reverse name: {{ family.reverse }}
{% endif %}
{{ family.actions }}

Generated on {% now "jS F Y \a\t H:i" %}
"""

reaction_family_name = "{{family.name}}"

# These lines were in the RMG library file but were not translated into anything useful:
unread_lines= """
{{ family.unread|safe|addslashes }}
"""

# Set some units for all the rates in this file

A_UNITS = "cm^3/mol/s"
E_UNITS = "kcal/mol"

# And these are the rates...

{% for rate in rates_for_table %}
# Number {{forloop.counter}}
rate({% for group in rate.group_definitions %}
  group{{ forloop.counter }} = 
"""
{{ group|safe }}""",{% endfor %}
  kf = Arrhenius(A=({{rate.A}},A_UNITS,"{{ rate.DA.toPython.0 }}",{{ rate.DA.toPython.1 }}),
                 n=({{rate.n}},None,"{{ rate.Dn.toPython.0 }}",{{ rate.Dn.toPython.1 }}),
                 alpha=({{rate.alpha}},None,"{{ rate.Dalpha.toPython.0 }}",{{ rate.Dalpha.toPython.1 }}),
                 E0=({{rate.E0}},E_UNITS,"{{ rate.DE0.toPython.0 }}",{{ rate.DE0.toPython.1 }})
                 ),
  temperature_range = ({{ rate.Tmin }},{{ rate.Tmax }}),
  rank = {{ rate.rank }},
  old_id = "{{ rate.id }}",
  short_comment = "{{ rate.comment|safe|addslashes }}",
  long_comment = 
"""
{{ rate.long_comment|safe|addslashes }}""",
   history = [("{% now "Y-m-d" %}","Generated from current RMG library.","rwest@mit.edu")]
)
{% endfor %}

