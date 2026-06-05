{{- define "cloudmaven.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "cloudmaven.fullname" -}}
{{- printf "%s-%s" .Release.Name .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "cloudmaven.image" -}}
{{- if .registry -}}
{{- printf "%s/%s:%s" .registry .image .tag -}}
{{- else -}}
{{- printf "%s:%s" .image .tag -}}
{{- end -}}
{{- end -}}

