# Helm chart repository for k8s-autoscaler-plugins

This is a bare Helm chart repository specifically for the [k8s-autoscaler-plugins](https://github.com/2i2c-org/k8s-autoscaler-plugins) chart.

{% for chartmap in site.data.index.entries %}
## Releases: {{ chartmap[0] }}

| Version | Date | App. version |
|---------|------|---------------------|
  {%- assign sortedcharts = chartmap[1] | sort: 'created' | reverse %}
  {%- for chart in sortedcharts %}
| [{{ chart.version }}]({{ chart.urls[0] }}) | {{ chart.created | date_to_long_string }} | {{ chart.appVersion }} |
  {%- endfor %}
{%- endfor %}
