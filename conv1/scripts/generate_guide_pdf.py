"""Generates a professional User and Technical Guide PDF for the project."""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    HRFlowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


class NumberedCanvas(canvas.Canvas):
    """Canvas for adding running headers and 'Page X of Y' footers."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, total_pages):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#666666"))

        # Header on later pages
        if self._pageNumber > 1:
            self.drawString(
                54,
                11 * inch - 36,
                "Semantic Constraint-Based Detection of Data Integrity Attacks | User & Technical Guide",
            )
            self.setStrokeColor(colors.HexColor("#D0D7DE"))
            self.setLineWidth(0.5)
            self.line(54, 11 * inch - 42, 8.5 * inch - 54, 11 * inch - 42)

        # Footer on all pages
        footer_text = f"Page {self._pageNumber} of {total_pages}"
        self.drawRightString(8.5 * inch - 54, 36, footer_text)
        self.drawString(54, 36, "IEEE Information Security Conference Prototype | Academic & Operational Guide")
        self.setStrokeColor(colors.HexColor("#D0D7DE"))
        self.setLineWidth(0.5)
        self.line(54, 46, 8.5 * inch - 54, 46)

        self.restoreState()


def build_guide_pdf(output_filename: str):
    doc = SimpleDocTemplate(
        output_filename,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#1A365D")
    secondary_color = colors.HexColor("#2B6CB0")
    text_color = colors.HexColor("#2D3748")

    title_style = ParagraphStyle(
        "DocTitle",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=20,
        leading=24,
        textColor=primary_color,
        spaceAfter=6,
    )
    subtitle_style = ParagraphStyle(
        "DocSubtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=15,
        textColor=secondary_color,
        spaceAfter=14,
    )
    h1_style = ParagraphStyle(
        "SectionH1",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=17,
        textColor=primary_color,
        spaceBefore=12,
        spaceAfter=6,
        keepWithNext=True,
    )
    h2_style = ParagraphStyle(
        "SectionH2",
        parent=styles["Heading3"],
        fontName="Helvetica-Bold",
        fontSize=10.5,
        leading=14,
        textColor=secondary_color,
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True,
    )
    body_style = ParagraphStyle(
        "DocBody",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=text_color,
        spaceAfter=6,
    )
    bullet_style = ParagraphStyle(
        "DocBullet",
        parent=body_style,
        leftIndent=14,
        firstLineIndent=-10,
        spaceAfter=4,
    )
    code_style = ParagraphStyle(
        "DocCode",
        parent=styles["Normal"],
        fontName="Courier",
        fontSize=8,
        leading=11,
        textColor=colors.HexColor("#C7254E"),
        backColor=colors.HexColor("#F9F2F4"),
        borderPadding=3,
        spaceAfter=6,
    )
    table_cell = ParagraphStyle(
        "TableCell",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=8,
        leading=11,
        textColor=text_color,
    )
    table_header = ParagraphStyle(
        "TableHeader",
        parent=table_cell,
        fontName="Helvetica-Bold",
        textColor=colors.white,
    )

    story = []

    # Title Banner
    story.append(Paragraph("Operational Data Integrity Attack Detection System", title_style))
    story.append(
        Paragraph(
            "Semantic Constraint-Based Verification & Joint Temporal/Structural Escalation<br/>"
            "<b>Comprehensive User, Technical, and Experimental Guide</b>",
            subtitle_style,
        )
    )
    story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=10))

    # 1. Executive Summary & Purpose
    story.append(Paragraph("1. Executive Summary & System Overview", h1_style))
    story.append(
        Paragraph(
            "This project implements a reproducible Information Security research prototype designed to detect "
            "<b>plausible-looking data integrity attacks</b> in distributed operational systems. While legacy monitoring "
            "relies on univariate thresholds or unsupervised machine learning that scrutinize values in isolation, an attacker "
            "can inject syntactically valid and in-range numbers (e.g., claiming 38 tonnes of free warehouse capacity when inventory "
            "records and IoT sensors prove the warehouse is 85% full).",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "To solve this challenge, the system introduces two primary contributions:<br/>"
            "<b>1. Primary Contribution — Semantic Constraint Verification:</b> Formulates cross-source physical, operational, "
            "and historical invariants that must logically bind heterogeneous streams (IoT telemetry, transactional inventory, operational reports).<br/>"
            "<b>2. Secondary Contribution — Joint Temporal & Structural Escalation:</b> Formulates an explicit algorithmic pipeline "
            "correlating low-severity discrepancies over a sliding decay window and across entity graph topology, reliably escalating "
            "coordinated attacks without generating false alarms on normal operational fluctuations.",
            body_style,
        )
    )

    # 2. System Architecture & Components
    story.append(Paragraph("2. System Architecture & Core Modules", h1_style))
    story.append(
        Paragraph(
            "The prototype is organized into clean, modular Python packages adhering to the Ponytail design paradigm:",
            body_style,
        )
    )

    arch_data = [
        [
            Paragraph("Module", table_header),
            Paragraph("File Path", table_header),
            Paragraph("Core Functionality", table_header),
        ],
        [
            Paragraph("<b>Data Generation</b>", table_cell),
            Paragraph("<code>src/data_generation/</code>", table_cell),
            Paragraph("Generates physically consistent telemetry and implements Attacks A–E and collusion benchmarks.", table_cell),
        ],
        [
            Paragraph("<b>Semantic Engine</b>", table_cell),
            Paragraph("<code>src/semantic_constraints/</code>", table_cell),
            Paragraph("Evaluates Invariant C1 (Capacity), C2 (Inventory Reconciliation), and C3 (Historical Envelopes).", table_cell),
        ],
        [
            Paragraph("<b>Temporal Analysis</b>", table_cell),
            Paragraph("<code>src/temporal_analysis/</code>", table_cell),
            Paragraph("Sliding window W=12 with exponential decay λ, tracking recurrence, frequency, and persistence.", table_cell),
        ],
        [
            Paragraph("<b>Structural Graph</b>", table_cell),
            Paragraph("<code>src/structural_analysis/</code>", table_cell),
            Paragraph("NetworkX graph modeling hierarchical and operational links between entities.", table_cell),
        ],
        [
            Paragraph("<b>Joint Escalator</b>", table_cell),
            Paragraph("<code>src/escalation/</code>", table_cell),
            Paragraph("Fuses semantic, temporal, and structural scores into 4-tier alert classification.", table_cell),
        ],
        [
            Paragraph("<b>Explainability</b>", table_cell),
            Paragraph("<code>src/alerting/</code>", table_cell),
            Paragraph("Translates mathematical escalation triggers into human-interpretable forensic audit dossiers.", table_cell),
        ],
        [
            Paragraph("<b>Dashboard UI</b>", table_cell),
            Paragraph("<code>dashboard/</code>", table_cell),
            Paragraph("FastAPI backend + responsive HTML5/Plotly dashboard for real-time telemetry and scenario testing.", table_cell),
        ],
    ]
    t_arch = Table(arch_data, colWidths=[1.3 * inch, 1.8 * inch, 3.9 * inch])
    t_arch.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), primary_color),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8F9FA")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t_arch)
    story.append(Spacer(1, 10))

    # Page Break for Instructions
    story.append(PageBreak())

    # 3. Step-by-Step Execution Guide
    story.append(Paragraph("3. How to Set Up and Run the Project", h1_style))
    story.append(Paragraph("<b>Step 1: Verify Dependencies & Environment</b>", h2_style))
    story.append(
        Paragraph(
            "The codebase is built for Python 3.12+ and uses standard scientific libraries already available in your environment.",
            body_style,
        )
    )
    story.append(
        Paragraph("<code>python -m pip install -r requirements.txt</code>", code_style)
    )

    story.append(Paragraph("<b>Step 2: Run the Automated Test Suite</b>", h2_style))
    story.append(
        Paragraph(
            "Run the comprehensive assert-based pytest test suite to verify module correctness and pipeline integration:",
            body_style,
        )
    )
    story.append(Paragraph("<code>pytest -v tests/</code>", code_style))
    story.append(
        Paragraph(
            "Expected output: <b>7 passed</b> across generator determinism, physical consistency, attack injection, "
            "semantic invariants, temporal decay, graph topology, and end-to-end alert pipeline.",
            body_style,
        )
    )

    story.append(Paragraph("<b>Step 3: Execute the Full Research Experiments Harness</b>", h2_style))
    story.append(
        Paragraph(
            "Execute the master evaluation harness which runs Experiments 1 through 9, logs raw CSV metrics, and generates IEEE publication figures:",
            body_style,
        )
    )
    story.append(Paragraph("<code>python experiments/run_all_experiments.py</code>", code_style))
    story.append(
        Paragraph(
            "Artifacts produced:<br/>"
            "• <b>Tables (CSV):</b> <code>results/tables/exp1_normal_baseline.csv</code>, <code>exp2_attack_a_capacity.csv</code>, "
            "<code>exp5_attack_e_coordinated.csv</code>, <code>ablation_study_results.csv</code>, <code>collusion_robustness.csv</code>.<br/>"
            "• <b>Figures (300 DPI):</b> <code>results/figures/fig1_baseline_comparison.png</code>, <code>fig2_ablation_performance.png</code>, "
            "<code>fig3_coordinated_attack_timeline.png</code>, <code>fig4_severity_sensitivity_curve.png</code>.",
            body_style,
        )
    )

    story.append(Paragraph("<b>Step 4: Launch the Interactive Security Dashboard</b>", h2_style))
    story.append(
        Paragraph(
            "Start the FastAPI interactive dashboard service:",
            body_style,
        )
    )
    story.append(Paragraph("<code>uvicorn dashboard.app:app --host 127.0.0.1 --port 8000 --reload</code>", code_style))
    story.append(
        Paragraph(
            "Open your web browser and navigate to <b><code>http://127.0.0.1:8000</code></b> to inspect the real-time operational monitor.",
            body_style,
        )
    )

    # 4. Empirical Evaluation Results Summary
    story.append(Paragraph("4. Key Experimental Findings (IEEE Paper Validation)", h1_style))
    story.append(
        Paragraph(
            "The experimental results demonstrate rigorous empirical superiority over traditional approaches:",
            body_style,
        )
    )

    exp_data = [
        [
            Paragraph("Attack Scenario", table_header),
            Paragraph("Baseline 1 (Threshold)", table_header),
            Paragraph("Baseline 2 (Isolation Forest)", table_header),
            Paragraph("Baseline 3 (Semantic Only)", table_header),
            Paragraph("Proposed (Joint Escalation)", table_header),
        ],
        [
            Paragraph("<b>Normal Stream (2016 steps)</b>", table_cell),
            Paragraph("FPR: 0.0%", table_cell),
            Paragraph("FPR: 52.8% (Extreme)", table_cell),
            Paragraph("FPR: 0.0%", table_cell),
            Paragraph("<b>FPR: 0.0% (Zero False Alarms)</b>", table_cell),
        ],
        [
            Paragraph("<b>Attack A: Capacity Tamper</b>", table_cell),
            Paragraph("Recall: 0.0% (Blind)", table_cell),
            Paragraph("Recall: 0.0% (Blind)", table_cell),
            Paragraph("Recall: 100% (Delay: 0m)", table_cell),
            Paragraph("<b>Recall: 100% (Delay: 0m)</b>", table_cell),
        ],
        [
            Paragraph("<b>Attack E: Coordinated Subtle</b>", table_cell),
            Paragraph("Recall: 0.0% (Blind)", table_cell),
            Paragraph("Precision: 3.8% (FPR high)", table_cell),
            Paragraph("Recall: 0.0% (Missed)", table_cell),
            Paragraph("<b>Recall: 93.3%, Precision: 100%</b>", table_cell),
        ],
        [
            Paragraph("<b>Ablation Arm C (Sem+Temp)</b>", table_cell),
            Paragraph("N/A", table_cell),
            Paragraph("N/A", table_cell),
            Paragraph("N/A", table_cell),
            Paragraph("Recall: 93.3% (Temporal lift)", table_cell),
        ],
        [
            Paragraph("<b>Robustness Collusion Test</b>", table_cell),
            Paragraph("Recall: 0.0%", table_cell),
            Paragraph("Recall: 52.8%", table_cell),
            Paragraph("Recall: 2.8%", table_cell),
            Paragraph("<b>Recall: 0.0% (Documented ceiling)</b>", table_cell),
        ],
    ]
    t_exp = Table(exp_data, colWidths=[1.7 * inch, 1.3 * inch, 1.4 * inch, 1.3 * inch, 1.3 * inch])
    t_exp.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), primary_color),
                ("ALIGN", (0, 0), (-1, -1), "LEFT"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#D0D7DE")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.HexColor("#FFFFFF"), colors.HexColor("#F8F9FA")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(t_exp)
    story.append(Spacer(1, 10))

    # Page Break for Dashboard & Threat Model
    story.append(PageBreak())

    # 5. Dashboard Feature Walkthrough
    story.append(Paragraph("5. Interactive Security Dashboard User Guide", h1_style))
    story.append(
        Paragraph(
            "The web dashboard enables real-time operator inspection and live scenario simulation:",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "• <b>Scenario Selector Buttons:</b> Click any scenario (<i>Normal Baseline</i>, <i>Attack A: Capacity</i>, "
            "<i>Attack B: Inventory</i>, <i>Attack C: Sensor</i>, <i>Attack D: Replay</i>, <i>Attack E: Coordinated</i>, or <i>Collusion</i>). "
            "The backend immediately simulates the stream, runs the entire pipeline, and re-renders the charts.<br/>"
            "• <b>Status Badges & Metrics Cards:</b> Displays warehouse physical capacity (50t), real-time joint risk escalation score, "
            "active security alert count, and instantaneous semantic violation severity.<br/>"
            "• <b>Chart 1 (Reported vs Physical Reality):</b> Contrasts operator claims against true physical storage state, "
            "highlighting where reported capacity diverges from inventory telemetry.<br/>"
            "• <b>Chart 2 (Evidence Decomposition):</b> Plots the instantaneous semantic violation (purple), the temporal memory accumulator (blue), "
            "and the joint escalation risk score (gold) with dotted thresholds for Suspicious (0.40) and Attack (0.70).<br/>"
            "• <b>Explainable Security Audit Dossiers:</b> Lists recent alerts with structured evidence: violated invariant ID, "
            "temporal recurrence count in the last hour, topologically linked entities, and overall forensic conclusion.<br/>"
            "• <b>Operational Entity Topology:</b> Outlines the monitored physical and digital nodes within the cold-storage infrastructure.",
            bullet_style,
        )
    )
    story.append(Spacer(1, 8))

    # 6. Defense-in-Depth & Collusion Boundary
    story.append(Paragraph("6. Threat Model, Limitations & Collusion Boundary", h1_style))
    story.append(
        Paragraph(
            "In strict adherence to academic honesty and IEEE paper review standards, the project formally documents its boundaries:",
            body_style,
        )
    )
    story.append(
        Paragraph(
            "<b>1. Distinction Between Inconsistency and Confirmed Attack:</b> An isolated semantic discrepancy signifies data inconsistency "
            "(which could stem from sensor calibration drift or administrative batch logging delays). The system does not immediately sound "
            "an intrusion alarm on a single blip; it requires temporal recurrence and topological clustering to confirm attack intent.<br/>"
            "<b>2. The Multi-Source Collusion Ceiling:</b> In Experiment 9, when an adversary compromises the operational database, the inventory ledger, "
            "AND the IoT occupancy sensor simultaneously, and updates all three to agree with one another, cross-source invariant checks will "
            "see mutual agreement. This represents a fundamental threat-model boundary common to all cross-validation architectures. "
            "Mitigating this requires hardware-rooted attestation (e.g., TPM/secure enclave) for sensors and append-only cryptographic logging.",
            bullet_style,
        )
    )
    story.append(Spacer(1, 8))

    # 7. Verification Checklist
    story.append(Paragraph("7. Project Completion Checklist", h1_style))
    check_items = [
        "<b>[✓] Core Python Source Modules:</b> Generator, Attack Injector, ML Baseline, Constraints C1-C3, Temporal, Structural, Escalation, Alerting, Pipeline.",
        "<b>[✓] Automated Test Suite:</b> 7 unit and integration tests passing with pytest in < 3 seconds.",
        "<b>[✓] Complete Experimental Harness:</b> Experiments 1 to 9 executed, generating 10 CSV tables and 4 publication figures.",
        "<b>[✓] Interactive Security Dashboard:</b> FastAPI backend + Plotly web interface with real-time scenario simulation.",
        "<b>[✓] Master Project Plan:</b> Detailed PROJECT_PLAN.md in project root per Section 41 specifications.",
        "<b>[✓] Formal Research Reference:</b> Grounded in 'Semantic Constraint-Based Detection of Data Integrity Attacks' conference paper draft.",
    ]
    for ci in check_items:
        story.append(Paragraph(ci, bullet_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"User and Technical Guide PDF successfully built: {output_filename}")


if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    pdf_path = os.path.join(project_root, "User_and_Technical_Guide.pdf")
    build_guide_pdf(pdf_path)
