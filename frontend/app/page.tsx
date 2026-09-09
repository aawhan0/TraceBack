'use client'

import { useState } from 'react'
import { ChevronDown, ChevronRight, CircleHelp, Database, FileText, FlaskConical, History, Play, Settings2, Sparkles } from 'lucide-react'
import styles from './page.module.css'

const evidence = [
  { title: 'Connection pool saturation', detail: 'Pool wait time increased from 42ms to 1.8s while active connections remained at the configured limit.', source: 'metrics/database/pool_wait_time' },
  { title: 'Slow query cluster', detail: 'Three query signatures account for 78% of database time during the incident window.', source: 'traces/query-signatures' },
  { title: 'Deployment correlation', detail: 'The first elevated wait events appeared 4 minutes after release 2025.04.18.2.', source: 'deployments/2025.04.18.2' },
]

export default function Page() {
  const [hasRun, setHasRun] = useState(true)
  const [openSection, setOpenSection] = useState<string | null>(null)
  const [mode, setMode] = useState('LLM')
  const [scenario, setScenario] = useState('Database pool exhaustion')
  const [model, setModel] = useState('llama3.2')

  return (
    <main className={styles.shell}>
      <aside className={styles.sidebar}>
        <div className={styles.brand}>TraceBack</div>
        <nav className={styles.nav} aria-label="Primary navigation">
          <div className={styles.navLabel}>WORKSPACE</div>
          <button className={`${styles.navItem} ${styles.active}`}><FlaskConical size={16} /> Investigate</button>
          <button className={styles.navItem}><History size={16} /> Runs</button>
          <button className={styles.navItem}><FileText size={16} /> Scenarios</button>
          <div className={styles.navLabel}>SYSTEM</div>
          <button className={styles.navItem}><Settings2 size={16} /> Settings</button>
        </nav>
        <div className={styles.sidebarBottom}>
          <div className={styles.statusDot} /> Local environment
          <span className={styles.version}>v0.7.4</span>
        </div>
      </aside>

      <section className={styles.content}>
        <header className={styles.topbar}>
          <div className={styles.breadcrumb}><span>TraceBack</span><ChevronRight size={13} /><strong>Investigate</strong></div>
          <button className={styles.helpButton} aria-label="Help"><CircleHelp size={17} /></button>
        </header>

        <div className={styles.page}>
          <div className={styles.eyebrow}>INCIDENT ANALYSIS</div>
          <div className={styles.headingRow}>
            <div>
              <h1>Investigate incident</h1>
              <p className={styles.subtitle}>Run a scenario through the TraceBack agent and inspect its reasoning.</p>
            </div>
            <div className={styles.runMeta}><span className={styles.greenDot} /> Ready to run</div>
          </div>

          <div className={styles.workspace}>
            <section className={styles.controlPanel} aria-label="Investigation controls">
              <div className={styles.sectionKicker}>CONFIGURATION</div>
              <label className={styles.field}>
                <span>Scenario</span>
                <select value={scenario} onChange={(event) => setScenario(event.target.value)}>
                  <option>Database pool exhaustion</option>
                  <option>Elevated API latency</option>
                  <option>Memory pressure after deploy</option>
                </select>
              </label>
              <div className={styles.field}>
                <span>Agent mode</span>
                <div className={styles.segmented} role="group" aria-label="Agent mode">
                  {['Baseline', 'LLM'].map((item) => <button key={item} className={mode === item ? styles.selected : ''} onClick={() => setMode(item)}>{item}</button>)}
                </div>
              </div>
              <label className={styles.field}>
                <span>Model</span>
                <select value={model} onChange={(event) => setModel(event.target.value)} disabled={mode === 'Baseline'}>
                  <option>llama3.2</option>
                  <option>qwen2.5</option>
                  <option>mistral</option>
                </select>
              </label>
              <div className={styles.divider} />
              <button className={styles.primaryButton} onClick={() => setHasRun(true)}><Play size={14} fill="currentColor" /> Run investigation</button>
              <p className={styles.helper}>Uses mock data for this frontend preview. No API request is made.</p>
            </section>

            <section className={styles.results} aria-live="polite">
              {!hasRun ? <div className={styles.emptyState}><Sparkles size={20} /><h2>Ready when you are</h2><p>Configure an incident and run the investigation to see the result.</p></div> : <>
                <div className={styles.resultHeader}><div><div className={styles.sectionKicker}>LATEST RESULT</div><h2>Root cause diagnosis</h2></div><span className={styles.complete}><span /> Completed</span></div>
                <div className={styles.diagnosis}><div><div className={styles.diagnosisLabel}>PASS</div><h3>Database connection pool exhaustion</h3><p>The application is saturating its database connection pool under concurrent load. Slow queries introduced in the latest deployment hold connections longer than expected, causing requests to queue and eventually time out.</p></div></div>
                <div className={styles.confidence}><span>Confidence</span><strong>0.87</strong></div>
                <div className={styles.checks}><div className={styles.sectionKicker}>EVALUATION CHECKS</div><div className={styles.checkRow}><span className={styles.checkIcon}>✓</span><span>Correctly identified the primary failure mode</span><b>pass</b></div><div className={styles.checkRow}><span className={styles.checkIcon}>✓</span><span>Diagnosis is supported by available evidence</span><b>pass</b></div><div className={styles.checkRow}><span className={styles.checkIcon}>✓</span><span>Suggested action is safe and reversible</span><b>pass</b></div></div>
                <div className={styles.accordions}>
                  <button className={styles.accordionButton} onClick={() => setOpenSection(openSection === 'evidence' ? null : 'evidence')}><span><Database size={15} /> Evidence <em>3 items</em></span>{openSection === 'evidence' ? <ChevronDown size={16} /> : <ChevronRight size={16} />}</button>
                  {openSection === 'evidence' && <div className={styles.evidenceList}>{evidence.map((item) => <div className={styles.evidenceItem} key={item.title}><div><strong>{item.title}</strong><p>{item.detail}</p><code>{item.source}</code></div><span className={styles.evidenceNumber}>evidence</span></div>)}</div>}
                  <button className={styles.accordionButton} onClick={() => setOpenSection(openSection === 'details' ? null : 'details')}><span><Settings2 size={15} /> Technical details</span>{openSection === 'details' ? <ChevronDown size={16} /> : <ChevronRight size={16} />}</button>
                  {openSection === 'details' && <div className={styles.details}><span>run_id</span><code>run_01HTB7QY2X9W</code><span>duration</span><code>8.42s</code><span>agent</span><code>{mode.toLowerCase()}</code><span>model</span><code>{model}</code></div>}
                </div>
              </>}
            </section>
          </div>
        </div>
      </section>
    </main>
  )
}
