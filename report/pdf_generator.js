import fs from "fs";
import puppeteer from "puppeteer";

// Load JSON created by Python worker
const reportData = JSON.parse(fs.readFileSync("report/report_data.json", "utf8"));

async function generatePDF() {
    const template = fs.readFileSync("report/report_template.html", "utf8");

    let keyFindingsHTML = "";
    for (const item of reportData.executive_summary.key_findings) {
        keyFindingsHTML += `<li>${item}</li>`;
    }

    const compiled = template
        .replace("{{overall_risk_score}}", reportData.executive_summary.overall_risk_score)
        .replace("{{domain}}", reportData.executive_summary.domain)
        .replace("{{scanned_at}}", reportData.executive_summary.scanned_at)
        .replace("{{key_findings}}", keyFindingsHTML)
        .replace("{{techstack}}", JSON.stringify(reportData.techstack, null, 2))
        .replace("{{dns_security}}", JSON.stringify(reportData.dns_security, null, 2))
        .replace("{{open_ports}}", JSON.stringify(reportData.open_ports, null, 2))
        .replace("{{subdomains}}", JSON.stringify(reportData.subdomains, null, 2))
        .replace("{{screenshot_path}}", reportData.screenshot_path);

    fs.writeFileSync("report/compiled_report.html", compiled);

    const browser = await puppeteer.launch();
    const page = await browser.newPage();

    await page.goto(`file://${process.cwd()}/report/compiled_report.html`, {
        waitUntil: "networkidle0"
    });

    await page.pdf({
        path: "report/ghosttrace_report.pdf",
        format: "A4",
        printBackground: true
    });

    await browser.close();
}

// Run automatically when Python calls this file
generatePDF();
