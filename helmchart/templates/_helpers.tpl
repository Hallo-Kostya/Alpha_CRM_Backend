{{- define "backend.fullname" -}}
{{ .Release.Name }}-{{ .Chart.Name }}
{{- end }}

{{- define "backend.name" -}}
{{ .Chart.Name }}
{{- end }}