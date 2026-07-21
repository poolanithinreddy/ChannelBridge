import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  NavLink,
  Navigate,
  Route,
  Routes,
  useNavigate,
  useParams,
} from "react-router-dom";
import {
  Activity,
  ArrowRight,
  BarChart3,
  BookOpen,
  Building2,
  CheckCircle2,
  ChevronRight,
  ClipboardCheck,
  FileSearch,
  History,
  LayoutDashboard,
  LogOut,
  Menu,
  RefreshCcw,
  Send,
  Settings,
  ShieldCheck,
  UploadCloud,
  Users,
  Webhook,
  XCircle,
} from "lucide-react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";
import { api, BASE, getToken, login } from "./api";
import type { Issue, Partner, Submission, User } from "./types";
const disclaimer =
  "ChannelBridge is an independent educational project. It is not affiliated with, endorsed by, or integrated with YouTube, Google, or any commercial streaming platform.";
function Badge({ value }: { value: string }) {
  return <span className={`badge ${value}`}>{value.replaceAll("_", " ")}</span>;
}
function Loading() {
  return (
    <div className="loading" aria-label="Loading">
      <i />
      <i />
      <i />
    </div>
  );
}
function ErrorBox({ error }: { error: Error }) {
  return (
    <div className="alert error">
      <XCircle size={18} />
      {error.message}
    </div>
  );
}
function Empty({ children }: { children: string }) {
  return (
    <div className="empty">
      <FileSearch />
      <p>{children}</p>
    </div>
  );
}
function Login() {
  const nav = useNavigate();
  const [email, setEmail] = useState("operator@channelbridge.local");
  const [password, setPassword] = useState("ChannelBridgeDemo!");
  const mutation = useMutation({
    mutationFn: () => login(email, password),
    onSuccess: () => window.location.assign("/"),
  });
  return (
    <main className="login">
      <section className="login-brand">
        <div className="mark">CB</div>
        <p className="eyebrow">Partner operations, connected</p>
        <h1>Move every catalog from first feed to launch ready.</h1>
        <p>
          Validate synthetic media catalogs, resolve integration issues, and
          keep onboarding teams aligned in one operational workspace.
        </p>
        <div className="signal">
          <Activity />
          <span>
            <b>Demo workspace</b>
            <small>8 fictional partners · JSON + XML</small>
          </span>
        </div>
      </section>
      <section className="login-card">
        <p className="eyebrow">Welcome to ChannelBridge</p>
        <h2>Sign in to the demo</h2>
        <p className="muted">Select a persona or enter a seeded account.</p>
        <div className="personas">
          {[
            ["operator@channelbridge.local", "Operator"],
            ["admin@northstar.example", "Partner admin"],
            ["admin@channelbridge.local", "Platform admin"],
          ].map(([mail, label]) => (
            <button
              key={mail}
              onClick={() => setEmail(mail)}
              className={email === mail ? "active" : ""}
            >
              {label}
            </button>
          ))}
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            mutation.mutate();
          }}
        >
          <label>
            Email
            <input
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              type="email"
              required
            />
          </label>
          <label>
            Password
            <input
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              type="password"
              required
            />
          </label>
          {mutation.error && <ErrorBox error={mutation.error} />}
          <button className="primary" disabled={mutation.isPending}>
            {mutation.isPending ? "Signing in…" : "Enter workspace"}
            <ArrowRight size={18} />
          </button>
        </form>
        <p className="micro">
          Fictional credentials for local demonstration only.
        </p>
      </section>
    </main>
  );
}
const nav = [
  ["/", "Overview", LayoutDashboard],
  ["/partners", "Partners", Building2],
  ["/submissions", "Submissions", UploadCloud],
  ["/analytics", "Analytics", BarChart3],
  ["/webhooks", "Webhooks", Webhook],
  ["/docs", "Documentation", BookOpen],
  ["/audit", "Audit history", History],
  ["/settings", "Settings", Settings],
] as const;
function Shell() {
  const q = useQuery({
    queryKey: ["me"],
    queryFn: () => api<User>("/auth/me"),
  });
  const [open, setOpen] = useState(false);
  const navigate = useNavigate();
  if (q.isLoading) return <Loading />;
  if (q.error) return <Navigate to="/login" />;
  return (
    <div className="shell">
      <aside className={open ? "open" : ""}>
        <div className="brand">
          <span className="mark">CB</span>
          <span>
            ChannelBridge<small>Integration operations</small>
          </span>
        </div>
        <nav aria-label="Main navigation">
          {nav.map(([to, label, Icon]) => (
            <NavLink
              to={to}
              key={to}
              end={to === "/"}
              onClick={() => setOpen(false)}
            >
              <Icon size={19} />
              {label}
            </NavLink>
          ))}
        </nav>
        <div className="aside-foot">
          <div className="avatar">
            {q.data?.name
              .split(" ")
              .map((x) => x[0])
              .join("")}
          </div>
          <div>
            <b>{q.data?.name}</b>
            <small>{q.data?.role.replaceAll("_", " ")}</small>
          </div>
          <button
            aria-label="Sign out"
            onClick={() => {
              localStorage.removeItem("cb_token");
              navigate("/login");
            }}
          >
            <LogOut size={18} />
          </button>
        </div>
      </aside>
      <main className="workspace">
        <header>
          <button className="menu" onClick={() => setOpen(!open)}>
            <Menu />
          </button>
          <div>
            <span className="live-dot" />
            Demo environment
          </div>
          <span className="role">
            <ShieldCheck size={15} />
            {q.data?.role.replaceAll("_", " ")}
          </span>
        </header>
        <div className="content">
          <Routes>
            <Route index element={<Overview user={q.data!} />} />
            <Route path="partners" element={<Partners />} />
            <Route path="partners/:id" element={<PartnerDetail />} />
            <Route path="partners/:id/upload" element={<Upload />} />
            <Route
              path="submissions"
              element={<Submissions user={q.data!} />}
            />
            <Route path="submissions/:id" element={<Report />} />
            <Route path="analytics" element={<Analytics />} />
            <Route path="docs" element={<Docs />} />
            <Route path="webhooks" element={<Webhooks />} />
            <Route path="audit" element={<Audit />} />
            <Route path="settings" element={<SettingsPage />} />
          </Routes>
        </div>
        <footer>{disclaimer}</footer>
      </main>
    </div>
  );
}
function Title({
  eyebrow,
  title,
  copy,
  action,
}: {
  eyebrow: string;
  title: string;
  copy: string;
  action?: React.ReactNode;
}) {
  return (
    <div className="title">
      <div>
        <p className="eyebrow">{eyebrow}</p>
        <h1>{title}</h1>
        <p>{copy}</p>
      </div>
      {action}
    </div>
  );
}
function Metric({
  label,
  value,
  note,
  icon: Icon,
}: {
  label: string;
  value: string | number;
  note: string;
  icon: typeof Activity;
}) {
  return (
    <article className="metric">
      <div>
        <p>{label}</p>
        <strong>{value}</strong>
        <small>{note}</small>
      </div>
      <span>
        <Icon />
      </span>
    </article>
  );
}
function Overview({ user }: { user: User }) {
  const isPlatform = user.role.startsWith("platform");
  const ops = useQuery({
    queryKey: ["ops"],
    queryFn: () => api<any>("/operations/dashboard"),
    enabled: isPlatform,
  });
  const partner = useQuery({
    queryKey: ["partner", user.partner_id],
    queryFn: () => api<Partner>(`/partners/${user.partner_id}`),
    enabled: !isPlatform && !!user.partner_id,
  });
  if (ops.isLoading || partner.isLoading) return <Loading />;
  if (ops.error) return <ErrorBox error={ops.error} />;
  const d = ops.data;
  return (
    <>
      <Title
        eyebrow="Tuesday, July 21"
        title={`Good morning, ${user.name.split(" ")[0]}.`}
        copy={
          isPlatform
            ? "Here’s what needs attention across partner integrations."
            : "Your launch-readiness workspace is up to date."
        }
        action={
          <NavLink
            className="primary link"
            to={
              isPlatform ? "/partners" : `/partners/${user.partner_id}/upload`
            }
          >
            <UploadCloud size={17} />
            {isPlatform ? "Review partners" : "Submit a feed"}
          </NavLink>
        }
      />
      {isPlatform ? (
        <>
          <section className="metrics">
            <Metric
              label="Active partners"
              value={d.total_partners}
              note="Across all onboarding stages"
              icon={Users}
            />
            <Metric
              label="Launch ready"
              value={d.launch_ready}
              note="Cleared for simulated launch"
              icon={CheckCircle2}
            />
            <Metric
              label="Need attention"
              value={d.blocked}
              note="Partner action required"
              icon={Activity}
            />
            <Metric
              label="Validation rate"
              value={`${d.validation_success_rate}%`}
              note={`${d.submissions} catalog submissions`}
              icon={ShieldCheck}
            />
          </section>
          <section className="grid two">
            <article className="panel">
              <div className="panel-head">
                <div>
                  <p className="eyebrow">Validation quality</p>
                  <h2>Errors by category</h2>
                </div>
                <NavLink to="/analytics">
                  View analytics <ChevronRight size={16} />
                </NavLink>
              </div>
              {d.errors_by_category.length ? (
                <div className="chart-row">
                  <ResponsiveContainer width="48%" height={250}>
                    <PieChart>
                      <Pie
                        data={d.errors_by_category}
                        dataKey="count"
                        nameKey="category"
                        innerRadius={62}
                        outerRadius={92}
                      >
                        {d.errors_by_category.map((_: any, i: number) => (
                          <Cell
                            key={i}
                            fill={
                              [
                                "#5b67f1",
                                "#ee9361",
                                "#3dbb98",
                                "#db5f72",
                                "#8a6fd1",
                              ][i % 5]
                            }
                          />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="legend">
                    {d.errors_by_category.map((x: any, i: number) => (
                      <div key={x.category}>
                        <i
                          style={{
                            background: [
                              "#5b67f1",
                              "#ee9361",
                              "#3dbb98",
                              "#db5f72",
                              "#8a6fd1",
                            ][i % 5],
                          }}
                        />
                        <span>{x.category.replaceAll("_", " ")}</span>
                        <b>{x.count}</b>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <Empty>No validation issues in this range.</Empty>
              )}
            </article>
            <Attention />
          </section>
        </>
      ) : (
        <PartnerHero partner={partner.data!} />
      )}
    </>
  );
}
function Attention() {
  const q = useQuery({
    queryKey: ["partners"],
    queryFn: () => api<Partner[]>("/partners"),
  });
  return (
    <article className="panel">
      <div className="panel-head">
        <div>
          <p className="eyebrow">Priority queue</p>
          <h2>Partners needing attention</h2>
        </div>
      </div>
      {q.data
        ?.filter((p) => p.status === "action_required")
        .map((p) => (
          <NavLink className="queue" to={`/partners/${p.id}`} key={p.id}>
            <div className="company">{p.name[0]}</div>
            <span>
              <b>{p.name}</b>
              <small>Validation corrections required</small>
            </span>
            <strong>{p.readiness_score}%</strong>
            <ChevronRight />
          </NavLink>
        ))}
    </article>
  );
}
function PartnerHero({ partner }: { partner: Partner }) {
  return (
    <section className="grid two">
      <article className="panel readiness">
        <p className="eyebrow">Launch readiness</p>
        <div
          className="score"
          style={
            {
              "--score": `${partner.readiness_score * 3.6}deg`,
            } as React.CSSProperties
          }
        >
          <span>
            {partner.readiness_score}
            <small>%</small>
          </span>
        </div>
        <h2>{partner.status.replaceAll("_", " ")}</h2>
        <NavLink to={`/partners/${partner.id}`}>
          View calculation <ArrowRight size={16} />
        </NavLink>
      </article>
      <article className="panel">
        <p className="eyebrow">Recommended next action</p>
        <h2>Resolve blocking feed issues</h2>
        <p>
          Review the latest validation report, correct catalog metadata, then
          upload with a new idempotency key.
        </p>
        <NavLink className="primary link" to={`/partners/${partner.id}/upload`}>
          Upload corrected feed
        </NavLink>
      </article>
    </section>
  );
}
function Partners() {
  const q = useQuery({
    queryKey: ["partners"],
    queryFn: () => api<Partner[]>("/partners"),
  });
  return (
    <>
      <Title
        eyebrow="Partner operations"
        title="Partner portfolio"
        copy="Track onboarding momentum and unblock integrations."
      />
      {q.isLoading ? (
        <Loading />
      ) : q.error ? (
        <ErrorBox error={q.error} />
      ) : (
        <div className="partner-grid">
          {q.data?.map((p) => (
            <NavLink
              to={`/partners/${p.id}`}
              className="partner-card"
              key={p.id}
            >
              <div className="partner-top">
                <div className="company">
                  {p.name
                    .split(" ")
                    .map((x) => x[0])
                    .join("")
                    .slice(0, 2)}
                </div>
                <Badge value={p.status} />
              </div>
              <h3>{p.name}</h3>
              <p>
                {p.feed_type.toUpperCase()} · {p.default_language} ·{" "}
                {p.default_territory}
              </p>
              <div className="progress">
                <span style={{ width: `${p.readiness_score}%` }} />
              </div>
              <footer>
                <span>Readiness</span>
                <b>{p.readiness_score}%</b>
              </footer>
            </NavLink>
          ))}
        </div>
      )}
    </>
  );
}
function PartnerDetail() {
  const { id } = useParams();
  const p = useQuery({
    queryKey: ["partner", id],
    queryFn: () => api<Partner>(`/partners/${id}`),
  });
  const r = useQuery({
    queryKey: ["readiness", id],
    queryFn: () => api<any>(`/partners/${id}/readiness`),
  });
  const s = useQuery({
    queryKey: ["subs", id],
    queryFn: () => api<Submission[]>(`/partners/${id}/submissions`),
  });
  if (p.isLoading || r.isLoading) return <Loading />;
  if (p.error) return <ErrorBox error={p.error} />;
  return (
    <>
      <Title
        eyebrow="Partner workspace"
        title={p.data!.name}
        copy="Onboarding, catalog quality, and launch readiness in one view."
        action={
          <NavLink className="primary link" to={`/partners/${id}/upload`}>
            <UploadCloud size={17} />
            Submit feed
          </NavLink>
        }
      />
      <section className="metrics">
        <Metric
          label="Readiness"
          value={`${r.data.score}%`}
          note={r.data.status.replaceAll("_", " ")}
          icon={ClipboardCheck}
        />
        <Metric
          label="Feed format"
          value={p.data!.feed_type.toUpperCase()}
          note="ChannelBridge schema 1.0"
          icon={FileSearch}
        />
        <Metric
          label="Submissions"
          value={s.data?.length || 0}
          note="Across onboarding"
          icon={Send}
        />
      </section>
      <section className="grid two">
        <article className="panel">
          <div className="panel-head">
            <div>
              <p className="eyebrow">Transparent scoring</p>
              <h2>Readiness calculation</h2>
            </div>
          </div>
          {r.data.calculation.map((x: any) => (
            <div className="check-row" key={x.title}>
              {x.status === "complete" ? (
                <CheckCircle2 className="ok" />
              ) : (
                <span className="open-circle" />
              )}
              <span>
                <b>{x.title}</b>
                <small>{x.status}</small>
              </span>
              <strong>
                +{x.earned}/{x.weight}
              </strong>
            </div>
          ))}
        </article>
        <article className="panel">
          <div className="panel-head">
            <div>
              <p className="eyebrow">Catalog activity</p>
              <h2>Recent submissions</h2>
            </div>
          </div>
          {s.data?.slice(0, 5).map((x) => (
            <NavLink
              className="table-row"
              to={`/submissions/${x.id}`}
              key={x.id}
            >
              <span>
                <b>{x.filename}</b>
                <small>{new Date(x.received_at).toLocaleDateString()}</small>
              </span>
              <Badge value={x.status} />
              <strong>
                {x.valid_records}/{x.record_count} valid
              </strong>
            </NavLink>
          ))}
        </article>
      </section>
    </>
  );
}
function Upload() {
  const { id } = useParams();
  const nav = useNavigate();
  const [file, setFile] = useState<File>();
  const [key, setKey] = useState<string>(crypto.randomUUID());
  const m = useMutation({
    mutationFn: async () => {
      const body = new FormData();
      body.append("file", file!);
      return api<Submission>(`/partners/${id}/submissions`, {
        method: "POST",
        headers: { "Idempotency-Key": key },
        body,
      });
    },
    onSuccess: (x) => nav(`/submissions/${x.id}`),
  });
  return (
    <>
      <Title
        eyebrow="Catalog ingestion"
        title="Submit a test feed"
        copy="Upload an independent ChannelBridge JSON or XML 1.0 catalog for deterministic validation."
      />
      <section className="panel form-panel">
        <div className="stepper">
          <span className="active">1</span>
          <i />
          <span>2</span>
          <i />
          <span>3</span>
          <small>Choose feed</small>
          <small>Validate</small>
          <small>Review</small>
        </div>
        <label className="drop">
          <UploadCloud />
          <b>{file?.name || "Choose a JSON or XML feed"}</b>
          <span>Maximum 10 MiB · external URLs are never fetched</span>
          <input
            type="file"
            accept=".json,.xml,application/json,text/xml"
            onChange={(e) => setFile(e.target.files?.[0])}
          />
        </label>
        <label>
          Idempotency key
          <input value={key} onChange={(e) => setKey(e.target.value)} />
          <small>Retry the identical payload safely with this same key.</small>
        </label>
        {m.error && <ErrorBox error={m.error} />}
        <button
          className="primary"
          disabled={!file || m.isPending}
          onClick={() => m.mutate()}
        >
          {m.isPending ? "Validating…" : "Submit for validation"}
          <ArrowRight size={18} />
        </button>
      </section>
    </>
  );
}
function Submissions({ user }: { user: User }) {
  const partners = useQuery({
    queryKey: ["partners"],
    queryFn: () => api<Partner[]>("/partners"),
  });
  const [pid, setPid] = useState(user.partner_id || 0);
  const effective = pid || partners.data?.[0]?.id;
  const q = useQuery({
    queryKey: ["subs", effective],
    queryFn: () => api<Submission[]>(`/partners/${effective}/submissions`),
    enabled: !!effective,
  });
  return (
    <>
      <Title
        eyebrow="Feed operations"
        title="Submission history"
        copy="Monitor validation outcomes, retries, and processing health."
      />
      {!user.partner_id && (
        <select
          value={effective}
          onChange={(e) => setPid(Number(e.target.value))}
        >
          {partners.data?.map((p) => (
            <option value={p.id}>{p.name}</option>
          ))}
        </select>
      )}
      <article className="panel table">
        <div className="table-head">
          <span>Feed</span>
          <span>Status</span>
          <span>Records</span>
          <span>Retries</span>
          <span>Received</span>
        </div>
        {q.data?.map((s) => (
          <NavLink
            to={`/submissions/${s.id}`}
            className="table-line"
            key={s.id}
          >
            <span>
              <b>{s.filename}</b>
              <small>{s.format.toUpperCase()}</small>
            </span>
            <Badge value={s.status} />
            <span>
              {s.valid_records}/{s.record_count}
            </span>
            <span>{s.retry_count}</span>
            <span>{new Date(s.received_at).toLocaleDateString()}</span>
          </NavLink>
        ))}
      </article>
    </>
  );
}
function Report() {
  const { id } = useParams();
  const qc = useQueryClient();
  const [filter, setFilter] = useState("all");
  const q = useQuery({
    queryKey: ["report", id],
    queryFn: () =>
      api<{ submission: Submission; issues: Issue[] }>(
        `/submissions/${id}/report`,
      ),
  });
  const retry = useMutation({
    mutationFn: () => api(`/submissions/${id}/retry`, { method: "POST" }),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["report", id] }),
  });
  if (q.isLoading) return <Loading />;
  if (q.error) return <ErrorBox error={q.error} />;
  const { submission, issues } = q.data!;
  const shown = issues.filter((i) => filter === "all" || i.severity === filter);
  return (
    <>
      <Title
        eyebrow={`Submission #${id}`}
        title="Validation report"
        copy={`${submission.filename} · ${submission.record_count} records checked`}
        action={
          <div className="actions">
            <a
              className="secondary link"
              href={`${BASE}/submissions/${id}/report.csv`}
              onClick={(e) => {
                e.preventDefault();
                fetch(e.currentTarget.href, {
                  headers: { Authorization: `Bearer ${getToken()}` },
                })
                  .then((r) => r.blob())
                  .then((b) => {
                    const a = document.createElement("a");
                    a.href = URL.createObjectURL(b);
                    a.download = `channelbridge-report-${id}.csv`;
                    a.click();
                  });
              }}
            >
              Download CSV
            </a>
            <button className="primary" onClick={() => retry.mutate()}>
              <RefreshCcw size={16} />
              Retry
            </button>
          </div>
        }
      />
      <section className="report-summary">
        <div>
          <CheckCircle2 />
          <b>{submission.valid_records}</b>
          <span>Valid records</span>
        </div>
        <div>
          <XCircle />
          <b>{submission.invalid_records}</b>
          <span>Invalid records</span>
        </div>
        <div>
          <Activity />
          <b>{issues.length}</b>
          <span>Total issues</span>
        </div>
        <div>
          <Badge value={submission.status} />
        </div>
      </section>
      <div className="filterbar">
        {["all", "error", "warning", "information"].map((x) => (
          <button
            className={filter === x ? "active" : ""}
            onClick={() => setFilter(x)}
          >
            {x}
          </button>
        ))}
      </div>
      {shown.length ? (
        <div className="issues">
          {shown.map((i) => (
            <article key={i.id} className="issue">
              <span className={`severity ${i.severity}`}>
                {i.severity[0].toUpperCase()}
              </span>
              <div>
                <header>
                  <code>{i.code}</code>
                  <Badge value={i.category} />
                  <span>
                    Record {i.row || "feed"} · {i.field || "general"}
                  </span>
                </header>
                <h3>{i.message}</h3>
                <p>
                  <b>How to fix:</b> {i.suggested_fix}
                </p>
                <NavLink to="/docs">
                  Open documentation <ArrowRight size={14} />
                </NavLink>
              </div>
              <span className={i.blocks_readiness ? "blocking" : "nonblocking"}>
                {i.blocks_readiness ? "Blocks readiness" : "Non-blocking"}
              </span>
            </article>
          ))}
        </div>
      ) : (
        <Empty>No issues match this filter.</Empty>
      )}
    </>
  );
}
function Analytics() {
  const q = useQuery({
    queryKey: ["analytics"],
    queryFn: () => api<any>("/analytics/overview"),
  });
  return (
    <>
      <Title
        eyebrow="Cross-partner intelligence"
        title="Integration analytics"
        copy="SQL-backed patterns across fictional onboarding history. Correlation does not establish causation."
      />
      {q.isLoading ? (
        <Loading />
      ) : q.error ? (
        <ErrorBox error={q.error} />
      ) : (
        <section className="grid two">
          <article className="panel">
            <p className="eyebrow">Validation patterns</p>
            <h2>Most frequent error codes</h2>
            {q.data.frequent_errors.map((x: any, i: number) => (
              <div className="bar-row">
                <span>{x.code}</span>
                <i>
                  <b
                    style={{
                      width: `${Math.max(8, (x.count / q.data.frequent_errors[0].count) * 100)}%`,
                    }}
                  />
                </i>
                <strong>{x.count}</strong>
              </div>
            ))}
          </article>
          <article className="panel">
            <p className="eyebrow">Operational load</p>
            <h2>Retries by partner</h2>
            {q.data.retries_by_partner.map((x: any) => (
              <div className="rank">
                <span>{x.partner}</span>
                <b>{x.retries}</b>
              </div>
            ))}
          </article>
        </section>
      )}
    </>
  );
}
function Docs() {
  const [term, setTerm] = useState("");
  const q = useQuery({
    queryKey: ["docs", term],
    queryFn: () =>
      api<any[]>(`/docs${term ? `?q=${encodeURIComponent(term)}` : ""}`),
  });
  return (
    <>
      <Title
        eyebrow="Self-service knowledge"
        title="Documentation center"
        copy="Specifications, error references, and troubleshooting runbooks."
      />
      <div className="search">
        <FileSearch />
        <input
          aria-label="Search documentation"
          placeholder="Search error code, topic, or keyword…"
          value={term}
          onChange={(e) => setTerm(e.target.value)}
        />
      </div>
      <div className="docs-grid">
        {q.data?.map((d) => (
          <article className="doc" key={d.id}>
            <Badge value={d.category} />
            <h2>{d.title}</h2>
            <p>{d.summary}</p>
            <details>
              <summary>Read article</summary>
              <p>{d.content}</p>
            </details>
          </article>
        ))}
      </div>
    </>
  );
}
function Webhooks() {
  return (
    <>
      <Title
        eyebrow="Integration simulator"
        title="Webhook delivery lab"
        copy="Test signed callbacks, bounded retries, and deterministic failures without external traffic."
      />
      <section className="grid two">
        <article className="panel">
          <p className="eyebrow">Safe by design</p>
          <h2>Internal receiver only</h2>
          <p>
            Demo endpoints are restricted to the Compose network or localhost.
            HMAC secrets are shown once and stored only as hashes.
          </p>
          <div className="callout">
            <ShieldCheck />
            <span>
              <b>Failure injection is simulated</b>
              <small>No third-party destination is contacted.</small>
            </span>
          </div>
        </article>
        <article className="panel">
          <p className="eyebrow">Retry policy</p>
          <h2>Observable delivery attempts</h2>
          <div className="timeline">
            <span />
            <div>
              <b>Attempt 1</b>
              <small>Immediate · HTTP 500 simulated</small>
            </div>
            <span />
            <div>
              <b>Attempt 2</b>
              <small>2.6 seconds · jitter applied</small>
            </div>
            <span className="ok" />
            <div>
              <b>Attempt 3</b>
              <small>4.2 seconds · HTTP 204</small>
            </div>
          </div>
        </article>
      </section>
    </>
  );
}
function Audit() {
  const q = useQuery({
    queryKey: ["audit"],
    queryFn: () => api<any[]>("/audit-events"),
  });
  return (
    <>
      <Title
        eyebrow="Governance"
        title="Audit history"
        copy="Important mutations and simulated operations with actor context."
      />
      <article className="panel">
        {q.data?.map((x) => (
          <div className="audit" key={x.id}>
            <span>
              <History />
            </span>
            <div>
              <b>{x.action.replaceAll(".", " ")}</b>
              <small>
                {x.entity_type} #{x.entity_id}
              </small>
            </div>
            <time>{new Date(x.created_at).toLocaleString()}</time>
          </div>
        ))}
      </article>
    </>
  );
}
function SettingsPage() {
  return (
    <>
      <Title
        eyebrow="Workspace controls"
        title="Settings"
        copy="Environment boundaries and security posture."
      />
      <section className="panel">
        <div className="setting">
          <div>
            <h3>Failure injection</h3>
            <p>Admin-only deterministic demo scenarios.</p>
          </div>
          <Badge value="disabled" />
        </div>
        <div className="setting">
          <div>
            <h3>External URL checks</h3>
            <p>Artwork URLs are syntax-checked but never fetched.</p>
          </div>
          <Badge value="disabled" />
        </div>
        <div className="setting">
          <div>
            <h3>Schema version</h3>
            <p>Independent ChannelBridge feed specification.</p>
          </div>
          <b>1.0</b>
        </div>
      </section>
    </>
  );
}
export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route
        path="/*"
        element={getToken() ? <Shell /> : <Navigate to="/login" />}
      />
    </Routes>
  );
}
