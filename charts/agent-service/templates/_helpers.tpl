{{/* Common labels */}}
{{- define "agent-service.labels" -}}
helm.sh/chart: {{ include "agent-service.chart" . }}
{{ include "agent-service.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/* Selector labels */}}
{{- define "agent-service.selectorLabels" -}}
app.kubernetes.io/name: {{ include "agent-service.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/* Full name */}}
{{- define "agent-service.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}