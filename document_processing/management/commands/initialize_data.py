from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from document_processing.models import Document
from document_generation.models import DocumentTemplate
import os

class Command(BaseCommand):
    help = 'Initialize the database with sample data'

    def handle(self, *args, **options):
        self.stdout.write('Initializing sample data...')
        
        # Create sample document templates
        self.create_document_templates()
        
        # Create sample documents
        self.create_sample_documents()
        
        self.stdout.write(self.style.SUCCESS('Sample data initialized successfully!'))
    
    def create_document_templates(self):
        """Create sample document templates"""
        if DocumentTemplate.objects.exists():
            self.stdout.write('Document templates already exist, skipping...')
            return
        
        # Create a contract template
        contract_template = DocumentTemplate.objects.create(
            name="Basic Contract Template",
            description="A simple contract template for general use",
            template_content="""
# CONTRACT AGREEMENT

## BETWEEN:
{{party_1_name}} ("Party 1")
AND
{{party_2_name}} ("Party 2")

## EFFECTIVE DATE:
{{effective_date}}

## TERMS AND CONDITIONS:

1. **SCOPE OF WORK**
   {{scope_of_work}}

2. **PAYMENT TERMS**
   {{payment_terms}}

3. **DURATION**
   This agreement shall commence on the Effective Date and continue until {{end_date}}, unless terminated earlier.

4. **CONFIDENTIALITY**
   Both parties agree to maintain the confidentiality of any proprietary information shared during the course of this agreement.

5. **TERMINATION**
   Either party may terminate this agreement with {{notice_period}} days written notice.

6. **GOVERNING LAW**
   This agreement shall be governed by the laws of {{jurisdiction}}.

## SIGNATURES:

Party 1: ________________________   Date: ____________
Party 2: ________________________   Date: ____________
            """,
            variables={
                "party_1_name": "Company Name",
                "party_2_name": "Client Name",
                "effective_date": "January 1, 2023",
                "scope_of_work": "Description of services to be provided",
                "payment_terms": "Payment amount and schedule",
                "end_date": "December 31, 2023",
                "notice_period": "30",
                "jurisdiction": "State of California"
            }
        )
        
        # Create a report template
        report_template = DocumentTemplate.objects.create(
            name="Business Report Template",
            description="A template for business reports and analyses",
            template_content="""
# {{report_title}}

## EXECUTIVE SUMMARY
{{executive_summary}}

## INTRODUCTION
{{introduction}}

## METHODOLOGY
{{methodology}}

## FINDINGS
{{findings}}

## ANALYSIS
{{analysis}}

## RECOMMENDATIONS
{{recommendations}}

## CONCLUSION
{{conclusion}}

## APPENDICES
{{appendices}}
            """,
            variables={
                "report_title": "Business Analysis Report",
                "executive_summary": "Brief summary of the entire report",
                "introduction": "Background and purpose of the report",
                "methodology": "Methods used to gather and analyze data",
                "findings": "Key findings from the research",
                "analysis": "Analysis of the findings",
                "recommendations": "Recommended actions based on the analysis",
                "conclusion": "Summary of key points and final thoughts",
                "appendices": "Additional supporting information"
            }
        )
        
        self.stdout.write(f'Created document templates: {contract_template.name}, {report_template.name}')
    
    def create_sample_documents(self):
        """Create sample documents"""
        if Document.objects.exists():
            self.stdout.write('Documents already exist, skipping...')
            return
        
        # Create a sample text document
        sample_text = """
SAMPLE AGREEMENT

This Agreement is made and entered into as of January 15, 2023, by and between ABC Corporation ("Company") and XYZ Ltd. ("Client").

1. SERVICES
   The Company agrees to provide the following services to the Client:
   - Strategic consulting
   - Market analysis
   - Competitive research

2. COMPENSATION
   Client agrees to pay Company $5,000 per month for the services described above.

3. TERM
   This Agreement shall commence on February 1, 2023 and continue for a period of 12 months.

4. CONFIDENTIALITY
   Both parties agree to maintain the confidentiality of all information shared during the course of this Agreement.

5. TERMINATION
   Either party may terminate this Agreement with 30 days written notice.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first above written.

ABC Corporation                    XYZ Ltd.
____________________              ____________________
By: John Smith                    By: Jane Doe
Title: CEO                        Title: President
        """
        
        text_doc = Document.objects.create(
            title="Sample Agreement",
            document_type="txt",
            extracted_text=sample_text,
            processing_status="completed"
        )
        
        # Create the actual file
        text_doc.file.save("sample_agreement.txt", ContentFile(sample_text.encode('utf-8')))
        
        # Create a sample report document
        sample_report = """
MARKET ANALYSIS REPORT

EXECUTIVE SUMMARY
This report analyzes the current market trends in the software industry, with a focus on AI and machine learning applications. The analysis shows significant growth opportunities in enterprise document automation.

INTRODUCTION
The software industry continues to evolve rapidly, with artificial intelligence and machine learning technologies driving innovation across sectors. This report examines current trends and future projections.

KEY FINDINGS
1. The global AI market is expected to grow at a CAGR of 40.2% from 2023 to 2030.
2. Document automation solutions are increasingly being adopted by enterprises to reduce manual processing time.
3. Integration of NLP capabilities is a key differentiator for leading solutions in the market.

RECOMMENDATIONS
1. Invest in developing advanced NLP capabilities for document understanding.
2. Focus on industry-specific solutions for legal, healthcare, and financial services.
3. Develop a robust API ecosystem to enable integration with existing enterprise systems.

CONCLUSION
The document automation market presents significant opportunities for growth, particularly when enhanced with AI capabilities. Companies that can deliver comprehensive, user-friendly solutions with advanced NLP features are likely to capture substantial market share.
        """
        
        report_doc = Document.objects.create(
            title="Market Analysis Report",
            document_type="txt",
            extracted_text=sample_report,
            processing_status="completed"
        )
        
        # Create the actual file
        report_doc.file.save("market_analysis.txt", ContentFile(sample_report.encode('utf-8')))
        
        self.stdout.write(f'Created sample documents: {text_doc.title}, {report_doc.title}') 