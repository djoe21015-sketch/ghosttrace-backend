// techstack_engine.cjs
// GhostTrace Techstack & Recon Engine (Phase 2 ready)

// --- Fetch wrapper for Node 24 / CommonJS ---
const fetch = (...args) =>
    import('node-fetch').then(({ default: fetch }) => fetch(...args));

// --- Required core modules ---
const fs = require('fs');
const path = require('path');

// If you use Puppeteer for screenshots:
let puppeteer;
try {
    puppeteer = require('puppeteer');
} catch (e) {
    puppeteer = null;
}

// --- Helper: safe JSON parse from stdin ---
function readStdinJSON() {
    return new Promise((resolve, reject) => {
        let data = '';
        process.stdin.setEncoding('utf8');
        process.stdin.on('data', chunk => (data += chunk));
        process.stdin.on('end', () => {
            try {
                const parsed = JSON.parse(data);
                resolve(parsed);
            } catch (err) {
                reject(new Error('Invalid JSON input: ' + err.toString()));
            }
        });
    });
}

// --- Core recon functions (simplified placeholders) ---

async function runBuiltWith(domain) {
    try {
        // Replace with your real BuiltWith logic
        const url = `https://${domain}`;
        const res = await fetch(url);
        const html = await res.text();
        return { html };
    } catch (err) {
        return { error: 'builtwith_failed', details: err.toString() };
    }
}

async function runWhatCMS(domain) {
    try {
        // Replace with your real WhatCMS logic
        return { cms: null, note: 'WhatCMS integration not implemented in this stub.' };
    } catch (err) {
        return { error: 'whatcms_failed', details: err.toString() };
    }
}

async function runWappalyzer(domain) {
    try {
        // Replace with your real Wappalyzer logic
        return { technologies: [], note: 'Wappalyzer integration not implemented in this stub.' };
    } catch (err) {
        return { error: 'wappalyzer_failed', details: err.toString() };
    }
}

async function runEnumeration(domain) {
    try {
        const url = `https://${domain}`;
        const res = await fetch(url);
        const html = await res.text();

        // Very basic enumeration
        const titleMatch = html.match(/<title[^>]*>([^<]*)<\/title>/i);
        const title = titleMatch ? titleMatch[1] : null;

        const scripts = (html.match(/<script[^>]*src=["']([^"']+)["'][^>]*>/gi) || [])
            .map(tag => {
                const m = tag.match(/src=["']([^"']+)["']/i);
                return m ? m[1] : 'inline';
            });

        const meta = (html.match(/<meta[^>]*>/gi) || []).map(tag => {
            const nameMatch = tag.match(/name=["']([^"']+)["']/i);
            const propMatch = tag.match(/property=["']([^"']+)["']/i);
            const contentMatch = tag.match(/content=["']([^"']+)["']/i);
            return {
                name: nameMatch ? nameMatch[1] : null,
                property: propMatch ? propMatch[1] : null,
                content: contentMatch ? contentMatch[1] : null
            };
        });

        const links = (html.match(/<link[^>]*>/gi) || []).map(tag => {
            const relMatch = tag.match(/rel=["']([^"']+)["']/i);
            const hrefMatch = tag.match(/href=["']([^"']+)["']/i);
            return {
                rel: relMatch ? relMatch[1] : null,
                href: hrefMatch ? hrefMatch[1] : null
            };
        });

        return { title, scripts, meta, links };
    } catch (err) {
        return { error: 'enumeration_failed', details: err.toString() };
    }
}

async function runTechDetected(domain, enumeration) {
    // Stub: you can enhance this later with real detection
    return {
        frontend: [],
        css: [],
        js: [],
        analytics: [],
        cdn: []
    };
}

async function runServerFingerprint(domain) {
    // Stub: you can replace with real TLS/port/cloud logic
    return {
        ip: null,
        reverse: [],
        tls: null
    };
}

async function runPorts(domain) {
    // Stub: you can replace with real port scanning
    return {
        80: { port: 80, status: 'open' },
        443: { port: 443, status: 'open' }
    };
}

async function runCloud(domain) {
    // Stub: you can replace with real cloud provider detection
    return {
        ip: null,
        reverse: [],
        provider: null
    };
}

async function runEmail(domain) {
    // Stub: you can replace with real MX/SPF/DMARC logic
    return {
        mx: [],
        spf: null,
        dkim: {},
        dmarc: []
    };
}

async function runSubdomains(domain) {
    // Stub: you can replace with real subdomain enumeration
    return {
        ct: [],
        dns: [],
        patterns: []
    };
}

async function runWhois(domain) {
    // Stub: you can replace with real WHOIS logic
    return {
        registrar: null,
        nameservers: [],
        status: null,
        registrant: null
    };
}

async function runHeaders(domain) {
    try {
        const url = `https://${domain}`;
        const res = await fetch(url);
        const headersObj = {};
        res.headers.forEach((value, key) => {
            headersObj[key] = value;
        });
        return {
            status: res.status,
            headers: headersObj,
            cookies: headersObj['set-cookie'] || null,
            cdn: null
        };
    } catch (err) {
        return { error: 'headerfinger_failed', details: err.toString() };
    }
}

async function runScreenshot(domain) {
    if (!puppeteer) {
        return { screenshot_base64: null, note: 'Puppeteer not available.' };
    }
    try {
        const browser = await puppeteer.launch();
        const page = await browser.newPage();
        await page.goto(`https://${domain}`, { waitUntil: 'networkidle2', timeout: 60000 });
        const buffer = await page.screenshot({ fullPage: true });
        await browser.close();
        return { screenshot_base64: buffer.toString('base64') };
    } catch (err) {
        return { screenshot_base64: null, error: err.toString() };
    }
}

// --- Report Builder (Phase 2 structured report) ---
function reportbuilder(data) {
    try {
        const {
            domain,
            builtwith,
            whatcms,
            wappalyzer,
            enumeration,
            techdetected,
            server,
            ports,
            cloud,
            email,
            subdomains,
            whois,
            headers,
            screenshot
        } = data;

        const executiveSummary = {
            domain,
            scanned_at: new Date().toISOString(),
            overall_risk_score: calculateRiskScore({ server, ports, email, subdomains }),
            key_findings: [
                server && server.tls ? `TLS ${server.tls.tlsVersion} with ${server.tls.cipher?.name}` : 'No TLS data available',
                cloud && cloud.provider ? `Cloud provider detected: ${cloud.provider}` : 'No cloud provider detected',
                email && email.dmarc && email.dmarc.length ? 'DMARC policy present' : 'No DMARC policy detected',
                ports
                    ? `Open ports: ${
                          Object.values(ports)
                              .filter(p => p.status === 'open')
                              .map(p => p.port)
                              .join(', ') || 'None'
                      }`
                    : 'No port data'
            ]
        };

        const technologyStack = {
            frontend: techdetected.frontend || [],
            css: techdetected.css || [],
            javascript: techdetected.js || [],
            analytics: techdetected.analytics || [],
            cdn: techdetected.cdn || [],
            cms: whatcms && !whatcms.error ? whatcms : null,
            raw_wappalyzer: wappalyzer && !wappalyzer.error ? wappalyzer : null,
            raw_builtwith: builtwith && !builtwith.error ? builtwith : null
        };

        const securityPosture = {
            tls: server && server.tls
                ? {
                      version: server.tls.tlsVersion,
                      cipher: server.tls.cipher,
                      certificate: server.tls.cert
                  }
                : null,
            server_ip: server && server.ip ? server.ip : null,
            reverse_dns: server && server.reverse ? server.reverse : [],
            cloud_provider: cloud && cloud.provider ? cloud.provider : null,
            headers: headers && !headers.error ? headers : null
        };

        const emailSecurity = {
            mx_records: email && email.mx ? email.mx : [],
            spf: email && email.spf ? email.spf : null,
            dkim: email && email.dkim ? email.dkim : {},
            dmarc: email && email.dmarc ? email.dmarc : [],
            risk_assessment: assessEmailRisk(email)
        };

        const subdomainExposure = {
            discovered_subdomains: subdomains && subdomains.dns ? subdomains.dns : [],
            pattern_guesses: subdomains && subdomains.patterns ? subdomains.patterns : [],
            ct_logs: subdomains && subdomains.ct ? subdomains.ct : []
        };

        const openPorts = {
            ports: ports ? Object.values(ports) : [],
            open: ports ? Object.values(ports).filter(p => p.status === 'open') : [],
            risky: ports ? Object.values(ports).filter(p => p.status === 'open' && isRiskyPort(p.port)) : []
        };

        const screenshotEvidence = {
            screenshot_base64: screenshot && screenshot.screenshot_base64 ? screenshot.screenshot_base64 : null,
            notes: enumeration && enumeration.title ? `Page title: ${enumeration.title}` : null
        };

        const recommendations = buildRecommendations({
            executiveSummary,
            securityPosture,
            emailSecurity,
            subdomainExposure,
            openPorts
        });

        const finalRisk = {
            score: executiveSummary.overall_risk_score,
            explanation: explainRiskScore(executiveSummary.overall_risk_score)
        };

        return {
            executive_summary: executiveSummary,
            technology_stack: technologyStack,
            security_posture: securityPosture,
            email_security: emailSecurity,
            subdomain_exposure: subdomainExposure,
            open_ports: openPorts,
            screenshot_evidence: screenshotEvidence,
            recommendations,
            final_risk: finalRisk
        };
    } catch (err) {
        return { error: 'report_generation_failed', details: err.toString() };
    }
}

// --- Risk & recommendation helpers ---

function isRiskyPort(port) {
    const risky = [21, 22, 23, 25, 53, 3306, 8080, 8443];
    return risky.includes(port);
}

function calculateRiskScore({ server, ports, email, subdomains }) {
    let score = 0;

    if (server && server.tls) {
        if (server.tls.tlsVersion === 'TLSv1.3') score += 15;
        else score += 5;
    }

    if (ports) {
        const open = Object.values(ports).filter(p => p.status === 'open');
        score += Math.max(0, 20 - open.length * 3);
    }

    if (email) {
        if (email.spf) score += 10;
        if (email.dmarc && email.dmarc.length) score += 10;
    }

    if (subdomains && subdomains.dns) {
        score += Math.max(0, 20 - subdomains.dns.length);
    }

    if (score > 100) score = 100;
    if (score < 0) score = 0;
    return score;
}

function assessEmailRisk(email) {
    if (!email) return 'unknown';

    const hasSPF = !!email.spf;
    const hasDMARC = email.dmarc && email.dmarc.length > 0;

    if (hasSPF && hasDMARC) return 'low';
    if (hasSPF && !hasDMARC) return 'medium';
    if (!hasSPF && hasDMARC) return 'medium';
    return 'high';
}

function buildRecommendations({ executiveSummary, securityPosture, emailSecurity, subdomainExposure, openPorts }) {
    const recs = [];

    if (emailSecurity.risk_assessment === 'high') {
        recs.push('Implement SPF, DKIM, and DMARC to reduce email spoofing risk.');
    } else if (emailSecurity.risk_assessment === 'medium') {
        recs.push('Review and strengthen email authentication (SPF/DMARC) policies.');
    }

    if (openPorts.risky && openPorts.risky.length > 0) {
        recs.push(`Review and restrict access to risky open ports: ${openPorts.risky.map(p => p.port).join(', ')}.`);
    }

    if (!securityPosture.tls || securityPosture.tls.version !== 'TLSv1.3') {
        recs.push('Upgrade TLS configuration to TLSv1.3 with modern ciphers.');
    }

    if (subdomainExposure.discovered_subdomains.length > 10) {
        recs.push('Audit exposed subdomains and decommission unused or legacy hosts.');
    }

    if (recs.length === 0) {
        recs.push('No critical issues detected. Maintain current security posture and monitor regularly.');
    }

    return recs;
}

function explainRiskScore(score) {
    if (score >= 80) return 'Low risk: strong security posture with minor improvements possible.';
    if (score >= 50) return 'Moderate risk: some security gaps should be addressed.';
    if (score >= 20) return 'High risk: multiple weaknesses present; remediation recommended.';
    return 'Critical risk: severe security issues; immediate action required.';
}

// --- MAIN ENGINE ---

async function main() {
    try {
        const input = await readStdinJSON();
        const domain = input.domain;

        const builtwith = await runBuiltWith(domain);
        const whatcms = await runWhatCMS(domain);
        const wappalyzer = await runWappalyzer(domain);
        const enumeration = await runEnumeration(domain);
        const techdetected = await runTechDetected(domain, enumeration);
        const server = await runServerFingerprint(domain);
        const ports = await runPorts(domain);
        const cloud = await runCloud(domain);
        const email = await runEmail(domain);
        const subdomains = await runSubdomains(domain);
        const whois = await runWhois(domain);
        const headers = await runHeaders(domain);
        const screenshot = await runScreenshot(domain);

        const fullData = {
            domain,
            builtwith,
            whatcms,
            wappalyzer,
            enumeration,
            techdetected,
            server,
            ports,
            cloud,
            email,
            subdomains,
            whois,
            headers,
            screenshot
        };

        const report = reportbuilder(fullData);

        const output = {
            ...fullData,
            report
        };

        console.log(JSON.stringify(output));
    } catch (err) {
        console.error(JSON.stringify({ error: err.toString() }));
        process.exit(1);
    }
}

main();
