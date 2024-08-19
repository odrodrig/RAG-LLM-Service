variable "project_name" {
  type    = string
  default = "rag-llm"
  description = "Name of Code Engine project"
}

variable "resource_group" {
  type    = string
  default = "rag-llm"
  description = "Resource group where project and application will reside"
}

variable "source_url" {
  type    = string
  default = ""
  description = "Git repo name"
}

variable "source_revision" {
  type    = string
  default = "main"
  description = "Git branch name"
}

variable "source_context_dir" {
  type    = string
  default = "application"
  description = "Subdirectory where Dockerfile and application files are located"
}

variable "cr_namespace" {
  type    = string
  default = "rag-images"
  description = "Container Registry namespace"
}

variable "cr_secret" {
  type        = string
  description = "Code Engine build secret"
  default = "buildsecret"
}

variable "cr_imagename" {
  type        = string
  description = "Code Engine build image"
  default = "rag-llm"
}

variable "ce_buildname" {
  type        = string
  description = "Code Engine build name"
  default = "rag-llm-build"
}

variable "ce_appname" {
  type        = string
  description = "Code Engine application name"
  default = "rag-llm-service"
}

variable "cos_ibm_cloud_api_key" {
  type        = string
  description = "COS API Key"
  default = ""
}

variable "cos_instance_id" {
  type        = string
  description = "COS Instance ID"
  default = ""
}

variable "cos_endpoint_url" {
  type        = string
  description = "COS endpoint"
  default = ""
}

variable "rag_app_api_key" {
  type        = string
  description = "RAG APP User Created Key"
  default = ""
}

variable "wx_project_id" {
  type        = string
  description = "watsonx project id"
  default = ""
}

variable "wx_url" {
  type        = string
  description = "watsonx URL with port number"
  default = ""
}

variable "wxd_username" {
  type        = string
  description = "watsonx discovery user"
  default = ""
}

variable "wxd_password" {
  type        = string
  description = "watsonx discovery password"
  default = ""
}

variable "wxd_url" {
  type        = string
  description = "watsonx discovery URL"
  default = ""
}

variable "wd_api_key" {
  type        = string
  description = "watson discovery apikey"
  default = "************"
}

variable "wd_url" {
  type        = string
  description = "watson discovery URL"
  default = "https://<url>"
}

variable "region" {
  description = "Region where Code Engine project will be created"
  type        = string
  default     = "us-south"
}
