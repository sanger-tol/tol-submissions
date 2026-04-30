{{/*
Expand the name of the chart.
*/}}
{{- define "submissions-app.name" -}}
{{- default .Chart.Name .Values.tolcore.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "submissions-app.fullname" -}}
{{- if .Values.tolcore.fullnameOverride }}
{{- .Values.tolcore.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.tolcore.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}


{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "submissions-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "submissions-app.labels" -}}
helm.sh/chart: {{ include "submissions-app.chart" . }}
{{ include "submissions-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "submissions-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "submissions-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "submissions-app.serviceAccountName" -}}
{{- if .Values.tolcore.serviceAccount.create }}
{{- default (include "submissions-app.fullname" .) .Values.tolcore.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.tolcore.serviceAccount.name }}
{{- end }}
{{- end }}
