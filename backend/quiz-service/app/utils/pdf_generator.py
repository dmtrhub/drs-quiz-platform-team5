from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime
import io


class PDFGenerator:

    @staticmethod
    def generate_quiz_report(quiz, results, output_path=None):
        """
        Generate a PDF report for a quiz with all results
        """
        if output_path:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
        else:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)

        elements = []

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2c3e50'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#34495e'),
            spaceAfter=12
        )

        title = Paragraph(f"Quiz Report: {quiz.get('title', 'Untitled Quiz')}", title_style)
        elements.append(title)
        elements.append(Spacer(1, 0.2 * inch))

        quiz_info = [
            ['Time Limit:', f"{quiz.get('duration_seconds', 0)} seconds"],
            ['Total Questions:', str(len(quiz.get('questions', [])))],
            ['Total Results:', str(len(results))],
            ['Report Generated:', datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')]
        ]

        info_table = Table(quiz_info, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#2c3e50')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#bdc3c7'))
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 0.3 * inch))

        leaderboard_heading = Paragraph("Leaderboard - Top Performers", heading_style)
        elements.append(leaderboard_heading)

        leaderboard_data = [['Rank', 'User ID', 'User', 'Score', 'Time (seconds)', 'Submitted At']]

        for idx, result in enumerate(results[:20], 1):  
            leaderboard_data.append([
                str(idx),
                str(result.get('user_id', 'N/A')),
                result.get('user_name', 'N/A'),
                f"{result.get('score', 0)}/{result.get('max_score', 0)}",
                str(result.get('time_spent_seconds', 0)),
                result.get('submitted_at', datetime.utcnow()).strftime('%Y-%m-%d %H:%M') if isinstance(result.get('submitted_at'), datetime) else 'N/A'
            ])

        leaderboard_table = Table(leaderboard_data, colWidths=[0.5 * inch, 0.9 * inch, 1.5 * inch, 0.9 * inch, 1.2 * inch, 1.5 * inch])
        leaderboard_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#ecf0f1')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#95a5a6')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
        ]))
        elements.append(leaderboard_table)

        doc.build(elements)

        if output_path:
            return output_path
        else:
            buffer.seek(0)
            return buffer

    @staticmethod
    def generate_user_result_report(quiz, result, user_info, output_path=None):
        """
        Generate a personalized PDF report for a single user's quiz result
        """
        if output_path:
            doc = SimpleDocTemplate(output_path, pagesize=A4)
        else:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4)

        elements = []
        styles = getSampleStyleSheet()

        title = Paragraph(f"Quiz Result Report", styles['Title'])
        elements.append(title)
        elements.append(Spacer(1, 0.3 * inch))

        info = [
            ['User:', f"{user_info.get('first_name', '')} {user_info.get('last_name', '')}"],
            ['Email:', user_info.get('email', 'N/A')],
            ['Quiz:', quiz.get('title', 'N/A')],
            ['Score:', f"{result.get('score', 0)} / {result.get('max_score', 0)} points"],
            ['Rank:', f"#{result.get('ranked_position', 'N/A')}"],
            ['Time Spent:', f"{result.get('time_spent_seconds', 0)} seconds"]
        ]

        info_table = Table(info, colWidths=[2 * inch, 4 * inch])
        info_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f4f8')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
        ]))
        elements.append(info_table)

        doc.build(elements)

        if output_path:
            return output_path
        else:
            buffer.seek(0)
            return buffer
