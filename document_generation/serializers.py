from rest_framework import serializers
from .models import DocumentTemplate, GeneratedDocument
from document_processing.serializers import DocumentListSerializer

class DocumentTemplateSerializer(serializers.ModelSerializer):
    """Serializer for the DocumentTemplate model"""
    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'description', 'template_content', 'variables', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class DocumentTemplateListSerializer(serializers.ModelSerializer):
    """Serializer for listing document templates"""
    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'description', 'created_at']

class GeneratedDocumentSerializer(serializers.ModelSerializer):
    """Serializer for the GeneratedDocument model"""
    template = DocumentTemplateListSerializer(read_only=True)
    source_documents = DocumentListSerializer(many=True, read_only=True)
    
    class Meta:
        model = GeneratedDocument
        fields = [
            'id', 'title', 'template', 'content', 'file', 'parameters',
            'source_documents', 'generation_status', 'error_message',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'file', 'generation_status', 'error_message', 'created_at', 'updated_at']

class GeneratedDocumentListSerializer(serializers.ModelSerializer):
    """Serializer for listing generated documents"""
    class Meta:
        model = GeneratedDocument
        fields = ['id', 'title', 'generation_status', 'created_at']

class DocumentGenerationSerializer(serializers.ModelSerializer):
    """Serializer for document generation requests"""
    template_id = serializers.IntegerField(required=False, write_only=True)
    document_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        write_only=True
    )
    prompt = serializers.CharField(required=True, write_only=True)
    
    class Meta:
        model = GeneratedDocument
        fields = ['id', 'title', 'template_id', 'document_ids', 'prompt', 'parameters']
        read_only_fields = ['id']
    
    def create(self, validated_data):
        template_id = validated_data.pop('template_id', None)
        document_ids = validated_data.pop('document_ids', [])
        prompt = validated_data.pop('prompt', '')
        
        # Add prompt to parameters
        parameters = validated_data.get('parameters', {})
        parameters['prompt'] = prompt
        validated_data['parameters'] = parameters
        
        # Create the generated document
        generated_document = GeneratedDocument.objects.create(**validated_data)
        
        # Set template if provided
        if template_id:
            from .models import DocumentTemplate
            try:
                template = DocumentTemplate.objects.get(id=template_id)
                generated_document.template = template
                generated_document.save()
            except DocumentTemplate.DoesNotExist:
                pass
        
        # Add source documents if provided
        if document_ids:
            generated_document.source_documents.set(document_ids)
        
        return generated_document 