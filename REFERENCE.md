# Reference
## Rules
<details><summary><code>client.rules.<a href="src/rulebricks/rules/client.py">solve</a>(...) -> DynamicResponsePayload</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Executes a single rule identified by a unique slug. The request and response formats are dynamic, dependent on the rule configuration. Optionally target a specific published version (e.g. `3`) or a release environment (e.g. `production`) via the `version` path segment; `latest` (the default) executes the current published version.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.rules.solve(
    slug="slug",
    version="version",
    request={
        "name": "John Doe",
        "age": 30,
        "email": "jdoe@acme.co"
    },
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique identifier for the resource.
    
</dd>
</dl>

<dl>
<dd>

**version:** `str` — The version of the resource to target: a published version number (e.g. `3`), a release environment slug (e.g. `production`, always lowercase), or `latest` (default) to use the current published version.
    
</dd>
</dl>

<dl>
<dd>

**request:** `DynamicRequestPayload` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.rules.<a href="src/rulebricks/rules/client.py">bulk_solve</a>(...) -> typing.List[BulkRuleResponseItem]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Executes a particular rule against multiple request data payloads provided in a list. Optionally target a specific published version (e.g. `3`) or a release environment (e.g. `production`) via the `version` path segment; `latest` (the default) executes the current published version.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.rules.bulk_solve(
    slug="slug",
    version="version",
    request=[
        {
            "name": "John Doe",
            "age": 30,
            "email": "jdoe@acme.co"
        },
        {
            "name": "Jane Doe",
            "age": 28,
            "email": "jane@example.com"
        }
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique identifier for the resource.
    
</dd>
</dl>

<dl>
<dd>

**version:** `str` — The version of the resource to target: a published version number (e.g. `3`), a release environment slug (e.g. `production`, always lowercase), or `latest` (default) to use the current published version.
    
</dd>
</dl>

<dl>
<dd>

**request:** `typing.List[DynamicRequestPayload]` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.rules.<a href="src/rulebricks/rules/client.py">parallel_solve</a>(...) -> ParallelSolveResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Executes multiple rules or flows in parallel based on a provided mapping of rule/flow slugs to payloads.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks, ParallelSolveRequestValue
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.rules.parallel_solve(
    request={
        "eligibility": ParallelSolveRequestValue(
            rule="1ef03ms",
        ),
        "offers": ParallelSolveRequestValue(
            flow="OvmsYwn",
        )
    },
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request:** `ParallelSolveRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Infra
<details><summary><code>client.infra.<a href="src/rulebricks/infra/client.py">status</a>() -> ScaleStatusResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Reports the fleet scale-up state. Worker counts reflect solvers that have actually joined the processing group and can accept work. Self-hosted deployments only.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.infra.status()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.infra.<a href="src/rulebricks/infra/client.py">scale</a>() -> ScaleStatusResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Pre-scales the deployment's solver fleet to its maximum capacity ahead of a large batch workload, so the first wave of requests never pays the scale-from-baseline window. Takes no request body: the target is always the deployment's own configured ceiling. The fleet stays warm for a bounded window (default 10 minutes; repeat calls refresh it), after which normal autoscaling reclaims the capacity - an unused warm-up costs at most that window. Poll the GET variant until `status` is `ready` before starting the batch. Self-hosted deployments only.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.infra.scale()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Flows
<details><summary><code>client.flows.<a href="src/rulebricks/flows/client.py">execute</a>(...) -> DynamicResponsePayload</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Execute a flow by its slug. Optionally target a specific published version (e.g. `3`) or a release environment (e.g. `production`) via the `version` path segment; `latest` (the default) executes the current published version.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.flows.execute(
    slug="slug",
    version="version",
    request={
        "name": "John Doe",
        "age": 30,
        "email": "jdoe@acme.co"
    },
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique identifier for the resource.
    
</dd>
</dl>

<dl>
<dd>

**version:** `str` — The version of the resource to target: a published version number (e.g. `3`), a release environment slug (e.g. `production`, always lowercase), or `latest` (default) to use the current published version.
    
</dd>
</dl>

<dl>
<dd>

**request:** `DynamicRequestPayload` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Decisions
<details><summary><code>client.decisions.<a href="src/rulebricks/decisions/client.py">query</a>(...) -> DecisionLogResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Query decision logs with support for the decision data query language, rule/status filters, date ranges, and pagination. The query language supports field comparisons (e.g., `alpha=0`, `score>10`), contains/not-contains (e.g., `name:John`, `status!:error`), boolean logic (`AND`, `OR`), and parentheses for grouping.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.decisions.query(
    search="status=200",
    rules="Lead Qualification,Pricing Calculator",
    flows="Loan Approval Flow",
    contexts="loans",
    trace="7db50259-31a0-42c1-aa3c-36409ad3c756",
    statuses="200,400,500",
    item_filter="customer.id=cst_8f3a12",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**search:** `typing.Optional[str]` — Decision data query language expression to filter logs by request/response data. Supports field comparisons (`field=value`, `field>10`), contains (`field:text`), not-contains (`field!:text`), boolean operators (`AND`, `OR`), and parentheses. A bare UUID or 32-hex term resolves as an execution/correlation-id lookup automatically.
    
</dd>
</dl>

<dl>
<dd>

**rules:** `typing.Optional[str]` — Comma-separated list of rule names, IDs, or slugs to filter logs by. Names match partially; IDs and slugs match exactly.
    
</dd>
</dl>

<dl>
<dd>

**flows:** `typing.Optional[str]` — Comma-separated list of flow names, IDs, or slugs to filter logs by. Matches only flow-level execution logs; the rule executions that ran inside a flow are separate records and are not included.
    
</dd>
</dl>

<dl>
<dd>

**contexts:** `typing.Optional[str]` — Comma-separated list of context names or slugs to filter logs by. Matches the rule and flow executions that were triggered by those contexts (batch and interactive updates).
    
</dd>
</dl>

<dl>
<dd>

**trace:** `typing.Optional[str]` — Execution-trace correlation id. Returns every decision log from one execution tree: pass a log's `decision.root_flow_execution_id` (or any `flow_execution_id` / `parallel_execution_id`, including a bulk run's per-item `item_execution_ids` entries) to retrieve the flow-level record plus all subflow and rule records from that run. On self-hosted deployments, a log's observability `trace_id` is also accepted. Combine with `rules` or `search` to narrow to a specific rule or payload within the run.
    
</dd>
</dl>

<dl>
<dd>

**statuses:** `typing.Optional[str]` — Comma-separated list of HTTP status codes to filter logs by.
    
</dd>
</dl>

<dl>
<dd>

**include_traces:** `typing.Optional[QueryDecisionsRequestIncludeTraces]` — When `true`, each flow record in the response includes a decompressed `path_trace` field: the run's executed steps with their full inputs and outputs (an object for single runs, a null-aligned array matching the request array for bulk runs). Off by default - traces are stored compressed and can be large, so only enable this when you need them. Ignored in count mode.
    
</dd>
</dl>

<dl>
<dd>

**item_filter:** `typing.Optional[str]` — Bulk payload filter in the form `path=value`. For each bulk record in the results (array-shaped request/response), keeps only the items whose payload value at `path` equals `value`, slicing the `request` and `response` arrays and every index-aligned field (`decision.item_execution_ids`, `decision.item_indexes`, `decision.success_idxs`, and `path_trace` when `include_traces=true`) in lockstep so input/output alignment is preserved. Filtered records gain a `matched_items` array with the surviving items' original zero-based positions. Paths use dot notation into each item (`customer.id`, `lines.0.sku`); prefix with `request.` or `response.` to match only that side (unprefixed paths match either side). Values compare as exact scalar strings (`status=200`, `approved=true`). Non-bulk records are returned unchanged; bulk records with no matching items are returned with empty item arrays. Typical use: combine with `search`, `flows`, or `trace` to locate a bulk run, then isolate one item's payloads and its `item_execution_ids` entry without tracking indexes. Ignored in count mode.
    
</dd>
</dl>

<dl>
<dd>

**start:** `typing.Optional[datetime.datetime]` — Start date for the query range (ISO8601 format). Hosted queries may span at most 90 days. Persistent self-hosted queries may use any range within local ClickHouse retention; PVC-less archive mode is limited to 7 days. Defaults to the applicable maximum before `end` (or before now).
    
</dd>
</dl>

<dl>
<dd>

**end:** `typing.Optional[datetime.datetime]` — End date for the query range (ISO8601 format). Defaults to now. When supplied without `start`, the query covers the preceding 90 days on hosted/table mode or 7 days in PVC-less archive mode.
    
</dd>
</dl>

<dl>
<dd>

**sort:** `typing.Optional[QueryDecisionsRequestSort]` — Column to sort results by. `time` orders by execution timestamp, `name` by rule/flow name, `status` by HTTP status code, and `type` by operation (solve, bulk-solve, flows, etc.). Defaults to `time`.
    
</dd>
</dl>

<dl>
<dd>

**order:** `typing.Optional[QueryDecisionsRequestOrder]` — Sort direction. Defaults to `desc`.
    
</dd>
</dl>

<dl>
<dd>

**cursor:** `typing.Optional[str]` — Opaque pagination token returned by the previous response. Pass it back verbatim to fetch the next page; do not construct or modify cursor values.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Number of results to return per page (default: 100, maximum: 1000). Logs carry full request/response payloads, so use smaller limits when querying workspaces with large bulk operations. Time-sorted pagination uses a keyset cursor, so its scan cost does not grow with page depth.
    
</dd>
</dl>

<dl>
<dd>

**count:** `typing.Optional[QueryDecisionsRequestCount]` — If set to 'true', returns only the count of matching logs instead of the log data.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Users
<details><summary><code>client.users.<a href="src/rulebricks/users/client.py">invite</a>(...) -> UserInviteResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Invite a new user to the organization or update role or user group data for an existing user.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.users.invite(
    email="newuser@example.com",
    role="developer",
    user_groups=[
        "group1",
        "group2"
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**email:** `str` — Email of the user to invite.
    
</dd>
</dl>

<dl>
<dd>

**role:** `typing.Optional[UserInviteRequestRole]` — System or custom role ID to assign to the user. Available system roles include 'admin', 'editor', and 'developer'.
    
</dd>
</dl>

<dl>
<dd>

**user_groups:** `typing.Optional[typing.List[str]]` — List of user group names or IDs to assign to the user. All specified groups must exist in your organization.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.users.<a href="src/rulebricks/users/client.py">list</a>() -> UserListResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all users (including the admin and all team members) in the organization with their details including email, name, API key, role, user groups, and join date.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.users.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.users.<a href="src/rulebricks/users/client.py">create</a>(...) -> CreateUserResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new user directly with a password, bypassing the email invitation flow. The user can immediately log in with the provided credentials.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.users.create(
    email="newuser@example.com",
    password="securePassword123",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**email:** `str` — Email address for the new user.
    
</dd>
</dl>

<dl>
<dd>

**password:** `str` — Password for the new user (minimum 8 characters). The user can log in immediately with this password.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — Display name for the user.
    
</dd>
</dl>

<dl>
<dd>

**role:** `typing.Optional[str]` — Role to assign to the user. Defaults to 'developer' if not specified.
    
</dd>
</dl>

<dl>
<dd>

**user_groups:** `typing.Optional[typing.List[str]]` — List of user group names or IDs to assign to the user.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Assets
<details><summary><code>client.assets.<a href="src/rulebricks/assets/client.py">get_usage</a>() -> UsageStatistics</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get the rule execution usage of your organization.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.assets.get_usage()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.assets.<a href="src/rulebricks/assets/client.py">import_rbm</a>(...) -> ImportManifestResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Import rules, flows, contexts, and values from an Rulebricks manifest file (*.rbm). Both plain manifests and compressed ones (the compress-json array form produced by exporting with `compress: true`) are accepted and detected automatically. Run Flow (subflow) references between flows in the manifest are resolved to the slugs, IDs, and published versions the flows receive in this workspace.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment
from rulebricks.assets import ImportManifestRequestManifest

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.assets.import_rbm(
    manifest=ImportManifestRequestManifest(
        version="1.0",
        rules=[
            {
                "name": "Pricing Rule",
                "slug": "pricing-rule"
            }
        ],
        flows=[
            {
                "name": "Onboarding Flow",
                "slug": "onboarding-flow"
            }
        ],
        entities=[
            {
                "name": "Customer",
                "slug": "customer"
            }
        ],
        values=[
            {
                "name": "tax_rate",
                "value": 0.08
            }
        ],
    ),
    conflict_strategy="update",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**manifest:** `ImportManifestRequestManifest` — The RBM manifest object containing assets to import. Asset objects inside the manifest intentionally preserve `.rbm`/database casing so exported manifests can be imported without rewriting asset payloads. A compressed manifest is also accepted: the JSON array produced by the compress-json library (for example, the contents of a compressed .rbm file exported with `compress: true`); it is detected and decompressed automatically.
    
</dd>
</dl>

<dl>
<dd>

**conflict_strategy:** `typing.Optional[ImportManifestRequestConflictStrategy]` — How to handle conflicts with existing assets. 'update' overwrites, 'skip' ignores, 'error' fails.
    
</dd>
</dl>

<dl>
<dd>

**target_folder_name:** `typing.Optional[str]` — Optional folder name to place imported assets into. Created if it doesn't exist.
    
</dd>
</dl>

<dl>
<dd>

**legacy_rule_mapping:** `typing.Optional[typing.Dict[str, ImportManifestRequestLegacyRuleMappingValue]]` — Optional mapping for legacy flow imports to reuse existing rules.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.assets.<a href="src/rulebricks/assets/client.py">export_rbm</a>(...) -> ExportRbmAssetsResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Export selected rules, flows, contexts, and values to an Rulebricks manifest file (*.rbm). Dependencies are resolved automatically: exporting a flow includes its rules, contexts, vocabulary values, and any flows referenced by Run Flow nodes (recursively). Set `compress: true` to receive the manifest in compressed form (a compress-json array), which is much smaller and can be saved directly as a .rbm file; the import endpoint accepts both forms.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.assets.export_rbm(
    root_type="rule",
    root_ids=[
        "pricing-rule",
        "eligibility-check"
    ],
    include_downstream=False,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**root_type:** `ExportManifestRequestRootType` — The type of root asset to export. All dependencies will be included.
    
</dd>
</dl>

<dl>
<dd>

**root_ids:** `typing.List[str]` — Array of IDs for the root assets to export. Dependencies are automatically resolved.
    
</dd>
</dl>

<dl>
<dd>

**include_downstream:** `typing.Optional[bool]` — For context exports, whether to include rules and flows bound to the context.
    
</dd>
</dl>

<dl>
<dd>

**manifest_name:** `typing.Optional[str]` — Optional name for the exported manifest.
    
</dd>
</dl>

<dl>
<dd>

**manifest_description:** `typing.Optional[str]` — Optional description for the exported manifest.
    
</dd>
</dl>

<dl>
<dd>

**preview_only:** `typing.Optional[bool]` — If true, returns a preview of what would be exported without the full data.
    
</dd>
</dl>

<dl>
<dd>

**compress:** `typing.Optional[bool]` — If true, the manifest in the response is returned in compressed form: the JSON array produced by the compress-json library instead of a plain object. Compressed manifests are substantially smaller, can be saved directly as a .rbm file, and are accepted by the import endpoint as-is. Intended for raw HTTP usage and file tooling; typed SDK clients should omit this flag, since the generated response type models the manifest as an object.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Values
<details><summary><code>client.values.<a href="src/rulebricks/values/client.py">list</a>(...) -> ListValuesResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve vocabulary values for the authenticated user. Results are scoped to the API key holder's user groups. Optionally filter by user group name or ID when the API key has access to that group. Use the 'include' parameter to control whether usage information is returned. Small workspaces may omit pagination to receive the full catalog as an array (legacy behavior); workspaces above the catalog threshold must paginate with 'limit'/'cursor', which returns { data, next_cursor, total? } ordered by name. The 'prefix' and 'type' filters narrow results to a collection or value type.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.values.list(
    include="usage",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name:** `typing.Optional[str]` — Query all vocabulary values containing a specific name
    
</dd>
</dl>

<dl>
<dd>

**prefix:** `typing.Optional[str]` — Only return values whose name starts with this collection prefix (e.g. 'Countries.').
    
</dd>
</dl>

<dl>
<dd>

**type:** `typing.Optional[str]` — Only return values of this type (string, number, boolean, list, date, function).
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Page size (default 100, max 1000). Providing limit or cursor switches the response to the paginated { data, next_cursor } envelope.
    
</dd>
</dl>

<dl>
<dd>

**cursor:** `typing.Optional[str]` — Opaque pagination cursor from a previous page's next_cursor.
    
</dd>
</dl>

<dl>
<dd>

**user_group:** `typing.Optional[str]` — Filter results by user group name or ID. The value is validated against workspace groups. Admin/unrestricted API keys can request any group-specific view; restricted API keys may only filter to one of their assigned groups and receive a 403 when filtering outside those groups.
    
</dd>
</dl>

<dl>
<dd>

**include:** `typing.Optional[str]` — Comma-separated list of additional data to include. Use 'usage' to include which rules reference each value.
    
</dd>
</dl>

<dl>
<dd>

**resolve:** `typing.Optional[bool]` — By default, payloads containing value-to-value references are returned materialized (references replaced with their resolved values). Pass 'false' to return stored payloads as-is, with { "$rb": "globalValue", "id": "..." } reference markers intact, so the reference graph round-trips.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.values.<a href="src/rulebricks/values/client.py">update</a>(...) -> UpdateValuesResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update existing vocabulary values or add new ones for the authenticated user. Supports both flat and nested object structures. Nested objects are automatically flattened using dot notation with keys preserved exactly as sent (e.g. nested 'user_profile.first_name' becomes the value name 'user_profile.first_name'). Writes are set-based upserts keyed by value name - existing values keep their ids, so rule references stay valid - and each call is idempotent, so retrying a failed request is always safe. Imports of any size go through this endpoint (POST /values/bulk is an equivalent alias): drive large dictionaries as a sequence of chunked calls, each bounded by your deployment's request body limit. Payloads may compose values from other values with reference markers: { "$ref": "<value name>" } references a value by name (existing values first, then values created by the same request), and { "$rb": "globalValue", "id": "<value id>" } references by id. A scalar payload may be a single reference; list payloads may mix literal items and references. References are validated (existence, type match, cycles) before anything is written. Workspaces at or below the catalog threshold receive the full value list back (legacy behavior); larger workspaces receive summary counts ({ created, updated, processed }).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.values.update(
    values={
        "Favorite Color": "blue",
        "Age": 30,
        "Is Student": False,
        "Hobbies": ["reading", "cycling"]
    },
    user_groups=[
        "marketing",
        "developers"
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**values:** `typing.Dict[str, typing.Any]` — A dictionary of keys and values to update or add. Supports both flat key-value pairs and nested objects. Nested objects are automatically flattened using dot notation with keys preserved exactly as sent (e.g. 'user.contact_info.email' stays 'user.contact_info.email'). Individual payloads may be value-to-value references (see ValueReference): a scalar payload may be a single { "$ref": "<value name>" } marker, and list payloads may mix literal items with reference markers.
    
</dd>
</dl>

<dl>
<dd>

**user_groups:** `typing.Optional[typing.List[str]]` — Optional array of user group names or IDs. If omitted and user belongs to user groups, values will be assigned to all user's user groups. Required if values should be restricted to specific user groups.
    
</dd>
</dl>

<dl>
<dd>

**metadata_by_name:** `typing.Optional[typing.Dict[str, typing.Dict[str, typing.Any]]]` — Optional metadata keyed by vocabulary value name. This is the canonical snake_case field; legacy clients may still send `metadataByName`. System-owned keys (managedBy, source, lockedReason, previousTokens, and archive/tombstone fields) are stripped from user payloads - managed provenance and archive state cannot be forged.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.values.<a href="src/rulebricks/values/client.py">delete</a>(...) -> DeleteValueResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific vocabulary value for the authenticated user by its ID. Deletion is blocked while the value is referenced by any rule or flow. Values whose entire payload references the deleted value are deleted with it (cascade), and list values referencing it lose the referencing items; both effects are reported in the response.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.values.delete(
    id="id",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — ID of the vocabulary value to delete
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.values.<a href="src/rulebricks/values/client.py">sync</a>(...) -> SyncValuesResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Declaratively makes a collection exactly equal to the payload. Values in the payload are upserted (Existing values keep their IDs), and values under the collection that are absent from the payload are archived by default. The `sync` endpoint supports uploading a particularly large amount of values (100k+) in chunks, using the `sync_id` parameter to track the run.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.values.sync(
    collection="Medical Codes",
    values={
        "A123": "A123",
        "B456": "B456",
        "C789": "C789"
    },
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**collection:** `str` — Collection path to sync (e.g. 'Medical Codes'). Only values under this path are affected.
    
</dd>
</dl>

<dl>
<dd>

**values:** `typing.Optional[typing.Dict[str, typing.Any]]` — Desired members of the collection, keyed relative to the collection path ('A123' becomes 'Medical Codes.A123'). Nested objects flatten with dot notation, and payloads may use ValueReference markers. An empty object empties the collection. May be omitted on a pure finalize call (sync_id + complete).
    
</dd>
</dl>

<dl>
<dd>

**sync_id:** `typing.Optional[str]` — Identifier for a chunked run. Repeat the call with the same sync_id for each chunk of the desired state; nothing is removed until a call with complete: true. Abandoned runs are purged after 24 hours without removing anything.
    
</dd>
</dl>

<dl>
<dd>

**complete:** `typing.Optional[bool]` — Marks the run as complete, triggering the removal sweep. Implicitly true when sync_id is omitted (single-request syncs), false otherwise.
    
</dd>
</dl>

<dl>
<dd>

**permanently_delete:** `typing.Optional[bool]` — Hard-delete removed values instead of archiving them. Removals still referenced by a rule, flow, or surviving value are archived instead and reported in 'blocked'. Self-hosted deployments retain tombstones regardless.
    
</dd>
</dl>

<dl>
<dd>

**dry_run:** `typing.Optional[bool]` — Compute and return the full diff without writing anything. Only supported for single-request syncs (omit sync_id).
    
</dd>
</dl>

<dl>
<dd>

**user_groups:** `typing.Optional[typing.List[str]]` — Optional array of user group names to assign to written values, matching POST /values.
    
</dd>
</dl>

<dl>
<dd>

**metadata_by_name:** `typing.Optional[typing.Dict[str, typing.Dict[str, typing.Any]]]` — Optional metadata keyed by FULL value name (including the collection prefix).
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Objects
<details><summary><code>client.objects.<a href="src/rulebricks/objects/client.py">list</a>() -> typing.List[WorkspaceObject]</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Lists the workspace's objects (JSON Schemas). Results are scoped to the API key holder's user groups, matching the visibility model of values, rules, and flows: group-restricted keys only see objects whose user_groups overlap theirs.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.objects.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.objects.<a href="src/rulebricks/objects/client.py">upsert</a>(...) -> UpsertObjectResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Creates or updates an object by ID or name and syncs enum values it generates. Objects help workspace admins programmatically determine multiple collections of values based on Rulebricks' contracts with external systems from a single JSON Schema source.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.objects.upsert(
    name="Claim",
    content="{\n  \"type\": \"object\",\n  \"properties\": {\n    \"countryCode\": { \"type\": \"string\", \"title\": \"Country Code\", \"enum\": [\"US\", \"CA\", \"GB\"] }\n  }\n}",
    user_groups=[
        "underwriting"
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**content:** `str` — The object's JSON Schema as a string. Enums in the schema become the object's managed values.
    
</dd>
</dl>

<dl>
<dd>

**id:** `typing.Optional[str]` — Object ID to update. Omit to resolve by name (creating the object when the name is new).
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — Object name. Required when ID is omitted; used to resolve the existing object or to name a new one.
    
</dd>
</dl>

<dl>
<dd>

**user_groups:** `typing.Optional[typing.List[str]]` — User groups for the object, propagated to every value it generates. Omit to keep the current groups.
    
</dd>
</dl>

<dl>
<dd>

**dry_run:** `typing.Optional[bool]` — Preview the value diff (would_sync / would_archive) without writing anything.
    
</dd>
</dl>

<dl>
<dd>

**expected_updated_at:** `typing.Optional[str]` — Optimistic concurrency: reject with 409 when the object's updated_at no longer matches.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.objects.<a href="src/rulebricks/objects/client.py">get</a>(...) -> WorkspaceObject</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Fetches one object by ID or exact name.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.objects.get(
    object_id="objectId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**object_id:** `str` — Object ID or exact name
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.objects.<a href="src/rulebricks/objects/client.py">delete</a>(...) -> DeleteObjectResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes the object. Its generated values always lose their management lock; by default they are also archived (published rules keep resolving them by id). Pass values=detach to keep them active as ordinary, hand-editable values instead. Requires the manage objects entitlement.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.objects.delete(
    object_id="objectId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**object_id:** `str` — Object ID or exact name
    
</dd>
</dl>

<dl>
<dd>

**values:** `typing.Optional[DeleteObjectsRequestValues]` — What happens to the values this object generated: 'archive' (default) or 'detach'.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Contexts
<details><summary><code>client.contexts.<a href="src/rulebricks/contexts/client.py">get</a>(...) -> ContextInstanceState</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve the current state of a context instance.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.contexts.get(
    slug="customer",
    instance="cust-12345",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique slug for the context.
    
</dd>
</dl>

<dl>
<dd>

**instance:** `str` — The unique identifier for the context instance.
    
</dd>
</dl>

<dl>
<dd>

**include_relations:** `typing.Optional[str]` — Comma-separated relationship names to include in the response under a 'relations' key (has_many relations return a list of related instance states; has_one/belongs_to return a single state or null). Use '*' for all relationships. Omitted by default - related instances are never fetched into the payload unrequested.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.contexts.<a href="src/rulebricks/contexts/client.py">submit</a>(...) -> SubmitContextDataResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Submit data to a context instance, creating it if it doesn't exist. May trigger bound rule/flow evaluations.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.contexts.submit(
    slug="customer",
    instance="cust-12345",
    request={
        "email": "customer@example.com",
        "age": 30
    },
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique slug for the context.
    
</dd>
</dl>

<dl>
<dd>

**instance:** `str` — The unique identifier for the context instance.
    
</dd>
</dl>

<dl>
<dd>

**request:** `SubmitContextDataRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.contexts.<a href="src/rulebricks/contexts/client.py">delete</a>(...) -> DeleteContextInstanceResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific context instance and its history.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.contexts.delete(
    slug="customer",
    instance="cust-12345",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique slug for the context.
    
</dd>
</dl>

<dl>
<dd>

**instance:** `str` — The unique identifier for the context instance.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.contexts.<a href="src/rulebricks/contexts/client.py">get_history</a>(...) -> ContextInstanceHistory</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve the change history for a context instance.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.contexts.get_history(
    slug="customer",
    instance="cust-12345",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique slug for the context.
    
</dd>
</dl>

<dl>
<dd>

**instance:** `str` — The unique identifier for the context instance.
    
</dd>
</dl>

<dl>
<dd>

**field:** `typing.Optional[str]` — Filter history to a specific field.
    
</dd>
</dl>

<dl>
<dd>

**limit:** `typing.Optional[int]` — Maximum number of history entries to return.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.contexts.<a href="src/rulebricks/contexts/client.py">get_pending</a>(...) -> ContextInstancePendingResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Get list of rules/flows that need to be evaluated for this instance.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.contexts.get_pending(
    slug="customer",
    instance="cust-12345",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique slug for the context.
    
</dd>
</dl>

<dl>
<dd>

**instance:** `str` — The unique identifier for the context instance.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.contexts.<a href="src/rulebricks/contexts/client.py">cascade</a>(...) -> CascadeContextResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Re-evaluate registered pending rule and flow executions for this instance after their fact or relationship dependencies may have become available. This does not run every bound asset.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.contexts.cascade(
    slug="customer",
    instance="cust-12345",
    request={},
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique slug for the context.
    
</dd>
</dl>

<dl>
<dd>

**instance:** `str` — The unique identifier for the context instance.
    
</dd>
</dl>

<dl>
<dd>

**request:** `CascadeContextRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.contexts.<a href="src/rulebricks/contexts/client.py">bulk_ingest</a>(...) -> ContextBatchResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Submit an array of records to any context in one synchronous call. Records merge into their context instances (matched by the context's identity fact), bound rules and flows whose inputs became satisfied execute, and the response returns the resolved state of every touched instance. Retries are always safe: merges are idempotent and executions are deduplicated by input hash. Fact history is recorded for tracked facts exactly as on individual writes. Clients chunk large datasets across requests. On the cloud platform, a batch may not exceed the plan's remaining monthly rule executions (402 above it) or a 4.5MB request body, and executed rules count toward plan usage. Private (self-hosted) deployments run batches through the high-performance server with no plan gating, a 10,000-records-per-request default cap (CONTEXT_BATCH_MAX_ITEMS), and NDJSON support (Content-Type: application/x-ndjson).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.contexts.bulk_ingest(
    slug="loan-application",
    request=[
        {
            "loan_id": "APP-1",
            "amount": 12000
        },
        {
            "loan_id": "APP-2",
            "amount": 7300
        }
    ],
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique slug for the context.
    
</dd>
</dl>

<dl>
<dd>

**request:** `typing.List[DynamicRequestPayload]` 
    
</dd>
</dl>

<dl>
<dd>

**include:** `typing.Optional[str]` — Comma-separated list of per-instance fields to include in results (instance_id is always present). Omit to include everything. Valid fields: positions, is_new, status, have, need, state, expires_at, executions, executed, triggered, reason. Useful for keeping response size proportional to outcomes rather than data volume, e.g. include=status,executed.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Assets Rules
<details><summary><code>client.assets.rules.<a href="src/rulebricks/assets/rules/client.py">delete</a>(...) -> SuccessMessage</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific rule by its ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.assets.rules.delete(
    id="2855f8da-2654-4df9-8903-8f797cbfe8eb",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The ID of the rule to delete.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.assets.rules.<a href="src/rulebricks/assets/rules/client.py">pull</a>(...) -> RuleExport</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Export a specific rule by its ID. This response preserves the raw rule document casing (for example, `requestSchema`, `sampleRequest`, and `createdAt`) so it can round-trip through `/admin/rules/import` and `.rbm` workflows.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.assets.rules.pull(
    id="2855f8da-2654-4df9-8903-8f797cbfe8eb",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The ID of the rule to export.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.assets.rules.<a href="src/rulebricks/assets/rules/client.py">push</a>(...) -> RuleExport</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create or update a rule. If `id` is provided, the matching rule is partially updated (all other fields optional). If `id` is omitted, a new rule is created (`id` and `slug` are auto-generated; all other fields required).
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks, RuleImportPayload, RuleImportSchemaField, RuleImportConditionRow, RuleImportRequestCell, RuleImportResponseCell, RuleImportRowSettings
from rulebricks.environment import RulebricksEnvironment
import datetime

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.assets.rules.push(
    rule=RuleImportPayload(
        name="Basic Pricing Rule",
        description="",
        created_at=datetime.datetime.fromisoformat("2026-02-12T01:29:23.000+00:00"),
        updated_at=datetime.datetime.fromisoformat("2026-02-12T01:29:23.000+00:00"),
        published=False,
        request_schema=[
            RuleImportSchemaField(
                key="customer_tier",
                show=True,
                name="Customer Tier",
                type="string",
            ),
            RuleImportSchemaField(
                key="order_total",
                show=True,
                name="Order Total",
                type="number",
            ),
            RuleImportSchemaField(
                key="expedited",
                show=True,
                name="Expedited",
                type="boolean",
            )
        ],
        response_schema=[
            RuleImportSchemaField(
                key="discount_rate",
                show=True,
                name="Discount Rate",
                type="number",
            ),
            RuleImportSchemaField(
                key="approval_status",
                show=True,
                name="Approval Status",
                type="string",
            )
        ],
        sample_request={
            "customer_tier": "STANDARD",
            "order_total": 250,
            "expedited": False
        },
        test_request={
            "customer_tier": "STANDARD",
            "order_total": 250,
            "expedited": False
        },
        sample_response={
            "discount_rate": 0,
            "approval_status": "standard"
        },
        conditions=[
            RuleImportConditionRow(
                request={
                    "customer_tier": RuleImportRequestCell(
                        op="equals",
                        args=[
                            "VIP"
                        ],
                    )
                },
                response={
                    "discount_rate": RuleImportResponseCell(
                        value=0.2,
                    ),
                    "approval_status": RuleImportResponseCell(
                        value="priority",
                    )
                },
                settings=RuleImportRowSettings(
                    enabled=True,
                    group_id=None,
                    priority=0,
                    schedule=[],
                ),
            ),
            RuleImportConditionRow(
                request={
                    "expedited": RuleImportRequestCell(
                        op="equals",
                        args=[
                            True
                        ],
                    )
                },
                response={
                    "discount_rate": RuleImportResponseCell(
                        value=0.05,
                    ),
                    "approval_status": RuleImportResponseCell(
                        value="expedited",
                    )
                },
                settings=RuleImportRowSettings(
                    enabled=True,
                    group_id=None,
                    priority=0,
                    schedule=[],
                ),
            ),
            RuleImportConditionRow(
                request={},
                response={
                    "discount_rate": RuleImportResponseCell(
                        value=0,
                    ),
                    "approval_status": RuleImportResponseCell(
                        value="standard",
                    )
                },
                settings=RuleImportRowSettings(
                    enabled=True,
                    group_id=None,
                    priority=0,
                    schedule=[],
                ),
            )
        ],
        history=[],
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**rule:** `RuleImportPayload` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.assets.rules.<a href="src/rulebricks/assets/rules/client.py">list</a>(...) -> RuleListResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all rules in the organization. Results are scoped to the API key holder's user groups. Optionally filter by folder name or ID, by user group name or ID when the API key has access to that group, or by name.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.assets.rules.list(
    folder="Marketing Rules",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**folder:** `typing.Optional[str]` — Filter results by folder name or folder ID.
    
</dd>
</dl>

<dl>
<dd>

**user_group:** `typing.Optional[str]` — Filter results by user group name or ID. The value is validated against workspace groups. Admin/unrestricted API keys can request any group-specific view; restricted API keys may only filter to one of their assigned groups and receive a 403 when filtering outside those groups.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — Filter results by name using a case-insensitive substring match.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Assets Flows
<details><summary><code>client.assets.flows.<a href="src/rulebricks/assets/flows/client.py">list</a>(...) -> FlowListResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all flows in the organization. Results are scoped to the API key holder's user groups. Optionally filter by folder name or ID, by user group name or ID when the API key has access to that group, or by name.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.assets.flows.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**folder:** `typing.Optional[str]` — Filter results by folder name or folder ID.
    
</dd>
</dl>

<dl>
<dd>

**user_group:** `typing.Optional[str]` — Filter results by user group name or ID. The value is validated against workspace groups. Admin/unrestricted API keys can request any group-specific view; restricted API keys may only filter to one of their assigned groups and receive a 403 when filtering outside those groups.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — Filter results by name using a case-insensitive substring match.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.assets.flows.<a href="src/rulebricks/assets/flows/client.py">push</a>(...) -> FlowImportResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create or update a flow from the Rulebricks Flow Schema (a list of `nodes` and `connections`). The server expands the Rulebricks Flow Schema definition into the full flow graph - laying it out, wiring property/control handles, resolving referenced published rules, and backfilling node defaults - so the result both renders in the editor and executes via `/flows/{slug}` without any manual editing. If `id` is provided the matching flow is updated; otherwise a new flow is created (`id`/`slug` auto-generated). Flows auto-publish unless `_publish` is set to `false`.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks, FlowImportPayload, RulebricksFlowNode, RulebricksFlowNodeCondition, RulebricksFlowNodeOutputsItem, RulebricksFlowConnection
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.assets.flows.push(
    flow=FlowImportPayload(
        name="Underwriting Flow",
        nodes=[
            RulebricksFlowNode(
                ref="input",
                type="origin",
                rule="customer-eligibility",
            ),
            RulebricksFlowNode(
                ref="gate",
                type="continue_if",
                condition=RulebricksFlowNodeCondition(
                    property="approved",
                    operator="equals",
                    args=[
                        True
                    ],
                ),
            ),
            RulebricksFlowNode(
                ref="enrich",
                type="code",
                outputs=[
                    RulebricksFlowNodeOutputsItem(
                        key="tier",
                        type="string",
                    )
                ],
                code="outputs.tier = inputs.score > 700 ? \'A\' : \'B\'",
            ),
            RulebricksFlowNode(
                ref="out",
                type="result",
                key="data",
            )
        ],
        connections=[
            RulebricksFlowConnection(
                from_="input",
                to="gate",
                output="approved",
            ),
            RulebricksFlowConnection(
                from_="input",
                to="enrich",
                output="score",
                input="score",
            ),
            RulebricksFlowConnection(
                from_="gate",
                to="out",
                control=True,
            ),
            RulebricksFlowConnection(
                from_="enrich",
                to="out",
                output="tier",
            )
        ],
        publish=True,
    ),
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**flow:** `FlowImportPayload` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.assets.flows.<a href="src/rulebricks/assets/flows/client.py">pull</a>(...) -> FlowImportPayload</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Export a flow into the Rulebricks Flow Schema (nodes + connections), the same shape accepted by `/admin/flows/import`. Works for flows built entirely by hand in the editor, so they can be round-tripped or version-controlled. This is distinct from the top-level `/admin/export`, which produces `.rbm` manifests.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.assets.flows.pull()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `typing.Optional[str]` — The ID of the flow to export (provide `id` or `slug`).
    
</dd>
</dl>

<dl>
<dd>

**slug:** `typing.Optional[str]` — The slug of the flow to export (provide `id` or `slug`).
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.assets.flows.<a href="src/rulebricks/assets/flows/client.py">delete</a>(...) -> SuccessMessage</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific flow by its ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.assets.flows.delete(
    id="3855f8da-2654-4df9-8903-8f797cbfe8ec",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The ID of the flow to delete.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Assets Folders
<details><summary><code>client.assets.folders.<a href="src/rulebricks/assets/folders/client.py">list</a>(...) -> FolderListResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve all rule folders for the authenticated user.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.assets.folders.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**user_group:** `typing.Optional[str]` — Filter results by user group name or ID. The value is validated against workspace groups. Admin/unrestricted API keys can request any group-specific view; restricted API keys may only filter to one of their assigned groups and receive a 403 when filtering outside those groups.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — Filter results by name using a case-insensitive substring match.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.assets.folders.<a href="src/rulebricks/assets/folders/client.py">upsert</a>(...) -> Folder</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new folder or update an existing one for the authenticated user. Folders are typed to organize rules (the default), flows, or contexts.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.assets.folders.upsert(
    name="Marketing Rules",
    description="Rules for marketing automation workflows",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name:** `str` — Name of the folder
    
</dd>
</dl>

<dl>
<dd>

**id:** `typing.Optional[str]` — Folder ID (required for updates, omit for creation)
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Description of the folder
    
</dd>
</dl>

<dl>
<dd>

**type:** `typing.Optional[UpsertFolderRequestType]` — The type of assets the folder organizes. Applies on creation; ignored when updating an existing folder.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.assets.folders.<a href="src/rulebricks/assets/folders/client.py">delete</a>(...) -> Folder</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific rule folder for the authenticated user. This does not delete the rules within the folder.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.assets.folders.delete(
    id="abc123",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — ID of the folder to delete
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Contexts Objects
<details><summary><code>client.contexts.objects.<a href="src/rulebricks/contexts/objects/client.py">list</a>(...) -> ContextListResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve all contexts for the authenticated user. Results are scoped to the API key holder's user groups. Optionally filter by folder name or ID, by user group name or ID when the API key has access to that group, or by name.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.contexts.objects.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**folder:** `typing.Optional[str]` — Filter results by folder name or folder ID.
    
</dd>
</dl>

<dl>
<dd>

**user_group:** `typing.Optional[str]` — Filter results by user group name or ID. The value is validated against workspace groups. Admin/unrestricted API keys can request any group-specific view; restricted API keys may only filter to one of their assigned groups and receive a 403 when filtering outside those groups.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — Filter results by name using a case-insensitive substring match.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.contexts.objects.<a href="src/rulebricks/contexts/objects/client.py">create</a>(...) -> CreateContextResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new context for the authenticated user.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks, ContextSchema, ContextSchemaField
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.contexts.objects.create(
    name="Customer",
    description="Represents a customer in the system",
    schema=ContextSchema(
        base=[
            ContextSchemaField(
                key="email",
                name="Email",
                type="string",
                required=True,
            ),
            ContextSchemaField(
                key="age",
                name="Age",
                type="number",
            )
        ],
        derived=[],
    ),
    identity_fact="email",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name:** `str` — The name of the context. The context's slug is generated from it (suffixed on collision).
    
</dd>
</dl>

<dl>
<dd>

**schema:** `ContextSchema` — The context's schema: an object with `base` (stored facts; at least one required) and optional `derived` (expression-computed facts) field arrays.
    
</dd>
</dl>

<dl>
<dd>

**identity_fact:** `str` — The fact key to use as the unique identifier for instances. Must be a key from schema.base.
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — The description of the context.
    
</dd>
</dl>

<dl>
<dd>

**auto_execute_decisions:** `typing.Optional[bool]` — When true (default), bound rules and flows automatically execute when their inputs are satisfied.
    
</dd>
</dl>

<dl>
<dd>

**ttl_seconds:** `typing.Optional[int]` — Time-to-live in seconds for live context instances (60 seconds to 30 days). Instances expire after this duration; each write extends the expiry.
    
</dd>
</dl>

<dl>
<dd>

**history_limit:** `typing.Optional[int]` — Maximum number of history entries to retain per field.
    
</dd>
</dl>

<dl>
<dd>

**on_schema_mismatch:** `typing.Optional[CreateContextRequestOnSchemaMismatch]` — How to handle submitted fields that don't match the schema: `ignore` drops them, `reject` fails the request (or the batch item), `store` persists them alongside declared facts.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.contexts.objects.<a href="src/rulebricks/contexts/objects/client.py">get</a>(...) -> ContextDetail</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieve a specific context by its ID.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.contexts.objects.get(
    id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The unique identifier for the context.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.contexts.objects.<a href="src/rulebricks/contexts/objects/client.py">update</a>(...) -> UpdateContextResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Update an existing context's properties and schema.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.contexts.objects.update(
    id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    name="Updated Customer",
    description="Updated description for premium customers",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The unique identifier for the context.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — The name of the context. Changing it regenerates the context's slug.
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — The description of the context.
    
</dd>
</dl>

<dl>
<dd>

**schema:** `typing.Optional[ContextSchema]` — Updated schema for the context: an object with `base` and optional `derived` field arrays.
    
</dd>
</dl>

<dl>
<dd>

**identity_fact:** `typing.Optional[str]` — The fact key to use as the unique identifier for instances. Must be a key from schema.base. Caution: changing this on a context with live instances changes how future writes resolve instances.
    
</dd>
</dl>

<dl>
<dd>

**auto_execute_decisions:** `typing.Optional[bool]` — When true, bound rules and flows automatically execute when their inputs are satisfied.
    
</dd>
</dl>

<dl>
<dd>

**ttl_seconds:** `typing.Optional[int]` — Time-to-live in seconds for live context instances (60 seconds to 30 days). Instances expire after this duration.
    
</dd>
</dl>

<dl>
<dd>

**history_limit:** `typing.Optional[int]` — Maximum number of history entries to retain per field.
    
</dd>
</dl>

<dl>
<dd>

**on_schema_mismatch:** `typing.Optional[UpdateContextRequestOnSchemaMismatch]` — How to handle submitted fields that don't match the schema: `ignore` drops them, `reject` fails the request (or the batch item), `store` persists them alongside declared facts.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.contexts.objects.<a href="src/rulebricks/contexts/objects/client.py">delete</a>(...) -> DeleteContextResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific context and all its instances.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.contexts.objects.delete(
    id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The unique identifier for the context.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Contexts Relationships
<details><summary><code>client.contexts.relationships.<a href="src/rulebricks/contexts/relationships/client.py">list</a>(...) -> ContextRelationshipsResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all relationships for a specific context.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.contexts.relationships.list(
    id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The unique identifier for the context.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.contexts.relationships.<a href="src/rulebricks/contexts/relationships/client.py">create</a>(...) -> CreateRelationshipResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new relationship between two contexts.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.contexts.relationships.create(
    id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    to_context_id="b2c3d4e5-f6a7-8901-bcde-f12345678901",
    relation_type="has_many",
    foreign_key_fact="customer_id",
    name="customer_orders",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The unique identifier for the context.
    
</dd>
</dl>

<dl>
<dd>

**to_context_id:** `str` — The ID of the target context.
    
</dd>
</dl>

<dl>
<dd>

**relation_type:** `CreateRelationshipRequestRelationType` — The type of relationship.
    
</dd>
</dl>

<dl>
<dd>

**foreign_key_fact:** `str` — The field key to use as the foreign key.
    
</dd>
</dl>

<dl>
<dd>

**name:** `typing.Optional[str]` — Optional runtime relationship key. It is normalized to lowercase snake_case; the target context slug is used when omitted.
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Description of the relationship.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.contexts.relationships.<a href="src/rulebricks/contexts/relationships/client.py">delete</a>(...) -> DeleteRelationshipResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Delete a specific relationship between contexts.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.contexts.relationships.delete(
    id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    relationship="c3d4e5f6-a7b8-9012-cdef-123456789012",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**id:** `str` — The unique identifier for the context.
    
</dd>
</dl>

<dl>
<dd>

**relationship:** `str` — The unique identifier for the relationship.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Tests Rules
<details><summary><code>client.tests.rules.<a href="src/rulebricks/tests/rules/client.py">list</a>(...) -> TestListResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieves a list of tests associated with the rule identified by the slug.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.tests.rules.list(
    slug="slug",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique identifier for the resource.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.tests.rules.<a href="src/rulebricks/tests/rules/client.py">create</a>(...) -> Test</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Adds a new test to the test suite of a rule identified by the slug.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.tests.rules.create(
    slug="slug",
    name="Test 3",
    request={
        "param1": "value1"
    },
    response={
        "status": "success"
    },
    critical=True,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique identifier for the resource.
    
</dd>
</dl>

<dl>
<dd>

**request:** `CreateTestRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.tests.rules.<a href="src/rulebricks/tests/rules/client.py">delete</a>(...) -> Test</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a test from the test suite of a rule identified by the slug.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.tests.rules.delete(
    slug="slug",
    test_id="testId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique identifier for the resource.
    
</dd>
</dl>

<dl>
<dd>

**test_id:** `str` — The ID of the test.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.tests.rules.<a href="src/rulebricks/tests/rules/client.py">run</a>(...) -> RunTestsResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Executes every test in the rule's test suite (or only the critical tests when `critical_only` is true) and returns a summary of which passed, which failed, and whether any CRITICAL test failed. Use the `critical_failure` flag as the signal for whether a release should be blocked. Tests always run against the latest draft of the rule; version targeting does not apply.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.tests.rules.run(
    slug="slug",
    critical_only=False,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique identifier for the resource.
    
</dd>
</dl>

<dl>
<dd>

**request:** `RunTestsRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Tests Flows
<details><summary><code>client.tests.flows.<a href="src/rulebricks/tests/flows/client.py">list</a>(...) -> TestListResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Retrieves a list of tests associated with the flow identified by the slug.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.tests.flows.list(
    slug="slug",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique identifier for the resource.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.tests.flows.<a href="src/rulebricks/tests/flows/client.py">create</a>(...) -> Test</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Adds a new test to the test suite of a flow identified by the slug.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.tests.flows.create(
    slug="slug",
    name="Test 3",
    request={
        "param1": "value1"
    },
    response={
        "status": "success"
    },
    critical=True,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique identifier for the resource.
    
</dd>
</dl>

<dl>
<dd>

**request:** `CreateTestRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.tests.flows.<a href="src/rulebricks/tests/flows/client.py">delete</a>(...) -> Test</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Deletes a test from the test suite of a flow identified by the slug.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.tests.flows.delete(
    slug="slug",
    test_id="testId",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique identifier for the resource.
    
</dd>
</dl>

<dl>
<dd>

**test_id:** `str` — The ID of the test.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.tests.flows.<a href="src/rulebricks/tests/flows/client.py">run</a>(...) -> RunTestsResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Executes every test in the flow's test suite (or only the critical tests when `critical_only` is true) against the flow's current graph and returns a summary of which passed, which failed, and whether any CRITICAL test failed. Tests always run against the latest draft of the flow; version targeting does not apply.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.tests.flows.run(
    slug="slug",
    critical_only=False,
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**slug:** `str` — The unique identifier for the resource.
    
</dd>
</dl>

<dl>
<dd>

**request:** `RunTestsRequest` 
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

## Users Groups
<details><summary><code>client.users.groups.<a href="src/rulebricks/users/groups/client.py">list</a>() -> UserGroupListResponse</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

List all user groups available in your Rulebricks organization.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.users.groups.list()

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

<details><summary><code>client.users.groups.<a href="src/rulebricks/users/groups/client.py">create</a>(...) -> UserGroup</code></summary>
<dl>
<dd>

#### 📝 Description

<dl>
<dd>

<dl>
<dd>

Create a new user group in your Rulebricks organization.
</dd>
</dl>
</dd>
</dl>

#### 🔌 Usage

<dl>
<dd>

<dl>
<dd>

```python
from rulebricks import Rulebricks
from rulebricks.environment import RulebricksEnvironment

client = Rulebricks(
    api_key="<value>",
    environment=RulebricksEnvironment.DEFAULT,
)

client.users.groups.create(
    name="NewGroup",
    description="Description of the new group.",
)

```
</dd>
</dl>
</dd>
</dl>

#### ⚙️ Parameters

<dl>
<dd>

<dl>
<dd>

**name:** `str` — Unique name of the user group.
    
</dd>
</dl>

<dl>
<dd>

**description:** `typing.Optional[str]` — Description of the user group.
    
</dd>
</dl>

<dl>
<dd>

**request_options:** `typing.Optional[RequestOptions]` — Request-specific configuration.
    
</dd>
</dl>
</dd>
</dl>


</dd>
</dl>
</details>

