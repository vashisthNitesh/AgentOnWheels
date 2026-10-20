<template>
  <div class="min-h-screen bg-app text-primary p-4 sm:p-6 lg:p-12 transition-colors duration-200 w-full max-w-full overflow-x-hidden">
    <ToastContainer />
    <ConfirmDialog />

    <div class="max-w-7xl mx-auto space-y-10 sm:space-y-14 w-full min-w-0">
      <!-- Header -->
      <div class="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border-default pb-6">
        <div class="min-w-0">
          <div class="flex flex-wrap items-center gap-2">
            <span class="text-xs uppercase tracking-wider font-semibold text-primary-600 dark:text-primary-400">Design System</span>
            <span class="chip bg-accent-50 text-accent-700 dark:bg-accent-950/50 dark:text-accent-300">Phase 2 Component Library</span>
          </div>
          <h1 class="text-2xl sm:text-3xl font-bold tracking-tight mt-1 break-words">Axle UI Primitives & Test Bench</h1>
          <p class="text-secondary text-sm mt-1">Enterprise-grade accessible components, form controls, feedback overlays, and tokens.</p>
        </div>

        <!-- Theme Mode Switcher -->
        <div role="radiogroup" aria-label="Theme mode" class="flex items-center gap-1 bg-surface border border-border-default rounded-lg p-1 shadow-xs shrink-0 self-start md:self-auto">
          <button
            v-for="mode in ['light', 'dark', 'system']"
            :key="mode"
            type="button"
            role="radio"
            :aria-checked="theme === mode"
            :class="[
              'px-3 py-1.5 text-xs font-medium rounded-md transition-all flex items-center gap-1.5 focus-ring cursor-pointer',
              theme === mode
                ? 'bg-primary-600 text-white shadow-xs dark:bg-primary-500'
                : 'text-secondary hover:text-primary hover:bg-subtle'
            ]"
            :aria-label="`Set theme to ${mode}`"
            @click="setTheme(mode)"
          >
            <component :is="modeIcon(mode)" class="w-3.5 h-3.5" />
            <span class="capitalize">{{ mode }}</span>
          </button>
        </div>
      </div>

      <!-- 1. Buttons Section -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold flex items-center gap-2">
          <span>🔘 Buttons (Variants & Sizes)</span>
        </h2>
        <Card class="p-6 space-y-6">
          <div class="space-y-2">
            <span class="text-xs font-mono text-muted uppercase tracking-wider">Variants</span>
            <div class="flex flex-wrap items-center gap-3">
              <Button variant="primary">Primary</Button>
              <Button variant="secondary">Secondary</Button>
              <Button variant="outline">Outline</Button>
              <Button variant="ghost">Ghost</Button>
              <Button variant="danger">Danger</Button>
              <Button variant="danger-ghost">Danger Ghost</Button>
              <Button variant="link">Link Style</Button>
            </div>
          </div>

          <div class="space-y-2">
            <span class="text-xs font-mono text-muted uppercase tracking-wider">States (Loading & Icons)</span>
            <div class="flex flex-wrap items-center gap-3">
              <Button variant="primary" :leading-icon="Plus">Create Order</Button>
              <Button variant="secondary" :trailing-icon="ArrowRight">Continue</Button>
              <Button variant="primary" loading>Saving Changes…</Button>
              <Button variant="danger" loading>Deleting…</Button>
              <Button variant="secondary" disabled>Disabled State</Button>
              <Button variant="secondary" size="icon" title="Settings" aria-label="Settings"><Settings class="w-4 h-4" /></Button>
            </div>
          </div>

          <div class="space-y-2">
            <span class="text-xs font-mono text-muted uppercase tracking-wider">Control Heights (32px, 36px, 40px)</span>
            <div class="flex flex-wrap items-center gap-3">
              <Button size="sm">Small (32px)</Button>
              <Button size="md">Medium (36px - Default)</Button>
              <Button size="lg">Large (40px)</Button>
            </div>
          </div>
        </Card>
      </section>

      <!-- 2. Form Controls Section -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold flex items-center gap-2">
          <span>📝 Form Controls & Accessible FormField</span>
        </h2>
        <Card class="p-4 sm:p-6 w-full min-w-0 overflow-hidden">
          <form @submit.prevent="toast.info('Form submitted successfully')" class="space-y-6">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <!-- Text Input with Units -->
            <FormField label="Cargo Weight" hint="Maximum payload capacity" required>
              <Input v-model="form.weight" type="number" suffix="tonnes" placeholder="0.00" clearable />
            </FormField>

            <!-- Currency with Prefix -->
            <FormField label="Target Sell Rate" optional>
              <Input v-model="form.rate" prefix="AED" placeholder="0.00" clearable />
            </FormField>

            <!-- Password with Caps Lock -->
            <FormField label="Driver Passcode" hint="Show/hide & Caps Lock detection" error="Passcode must be at least 6 digits">
              <Input v-model="form.password" type="password" placeholder="Enter secure passcode" autocomplete="new-password" />
            </FormField>

            <!-- Select Static Options -->
            <FormField label="Service Type" required>
              <Select
                v-model="form.serviceType"
                :options="[
                  { value: 'FTL', label: 'Full Truckload (FTL)', description: 'Dedicated fleet vehicle' },
                  { value: 'LTL', label: 'Less Than Truckload (LTL)', description: 'Shared cargo consolidation' },
                  { value: 'FCL', label: 'Full Container Load (FCL)', description: 'Standard container line' },
                ]"
                placeholder="Choose service type…"
                clearable
              />
            </FormField>

            <!-- Searchable Combobox -->
            <FormField label="Assign Customer (Combobox)" hint="Searchable with recent memory">
              <Combobox
                v-model="form.customerId"
                :options="mockCustomers"
                placeholder="Search or pick customer…"
                value-key="id"
                label-key="name"
              />
            </FormField>

            <!-- MultiSelect with Chips -->
            <FormField label="Required Documents (MultiSelect)">
              <MultiSelect
                v-model="form.docTypes"
                :options="mockDocs"
                placeholder="Select required documents…"
                value-key="id"
                label-key="name"
              />
            </FormField>

            <!-- DatePicker -->
            <FormField label="Loading Date & Time" required>
              <DatePicker v-model="form.loadingDate" with-time clearable />
            </FormField>

            <!-- DateRangePicker -->
            <FormField label="Reporting Window">
              <DateRangePicker
                v-model:start-value="form.startDate"
                v-model:end-value="form.endDate"
              />
            </FormField>

            <!-- Textarea -->
            <FormField label="Special Handling Instructions" optional>
              <Textarea v-model="form.notes" placeholder="Driver remarks, gate requirements…" :maxlength="300" />
            </FormField>
          </div>

          <!-- Checkbox, Switch, RadioGroup -->
          <div class="mt-8 pt-6 border-t border-border-default grid grid-cols-1 md:grid-cols-3 gap-6 items-start">
            <div class="space-y-3">
              <span class="text-xs font-mono text-muted uppercase tracking-wider block">Checkbox & Switch</span>
              <Checkbox v-model="form.isHazardous" label="Hazardous Materials (HAZMAT)" />
              <Checkbox model-value="indeterminate" label="Indeterminate Leg Allocation" />
              <Switch v-model="form.autoDispatch" label="Auto-dispatch on confirmation" description="Instantly allocate nearest verified truck" />
            </div>

            <div class="md:col-span-2 space-y-2">
              <span class="text-xs font-mono text-muted uppercase tracking-wider block">RadioGroup (Card Style)</span>
              <RadioGroup
                v-model="form.billingType"
                orientation="horizontal"
                :options="[
                  { value: 'per_trip', label: 'Per Trip Rate', description: 'Flat agreed rate per lane' },
                  { value: 'per_tonne', label: 'Per Tonne-Km', description: 'Dynamic weight & distance billing' },
                  { value: 'lease', label: 'Dedicated Lease', description: 'Monthly fixed contract vehicle' },
                ]"
              />
            </div>
          </div>
        </form>
      </Card>
      </section>

      <!-- 3. Status Vocabulary & Badges -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold flex items-center gap-2">
          <span>🏷️ Badges & StatusPill System</span>
        </h2>
        <Card class="p-6 space-y-6">
          <div class="space-y-2">
            <span class="text-xs font-mono text-muted uppercase tracking-wider">Semantic Badges</span>
            <div class="flex flex-wrap items-center gap-2">
              <Badge variant="neutral" dot>Neutral</Badge>
              <Badge variant="primary" dot>Primary</Badge>
              <Badge variant="accent" dot>Accent</Badge>
              <Badge variant="success" dot>Success</Badge>
              <Badge variant="warning" dot>Warning</Badge>
              <Badge variant="danger" dot>Danger</Badge>
              <Badge variant="info" dot>Info</Badge>
            </div>
          </div>

          <div class="space-y-2">
            <span class="text-xs font-mono text-muted uppercase tracking-wider">Status Pills (Tone Mapped with Live Pulse)</span>
            <div class="flex flex-wrap items-center gap-2.5">
              <StatusPill status="in_transit" show-icon />
              <StatusPill status="in_progress" show-icon />
              <StatusPill status="confirmed" show-icon />
              <StatusPill status="delivered" show-icon />
              <StatusPill status="completed" show-icon />
              <StatusPill status="pending" show-icon />
              <StatusPill status="unassigned" show-icon />
              <StatusPill status="cancelled" show-icon />
              <StatusPill status="ready_for_invoice" show-icon />
              <StatusPill status="paid" show-icon />
            </div>
          </div>
        </Card>
      </section>

      <!-- 4. Data Display, Avatars & KPIs -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold flex items-center gap-2">
          <span>📊 KPIs, Avatars & Micro-components</span>
        </h2>
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <KpiCard
            label="Total Orders"
            value="1,248"
            :delta="14.2"
            delta-period="vs last month"
            subtitle="98% on-time delivery"
            :sparkline="[20, 24, 30, 28, 35, 42, 48, 52]"
            clickable
          />
          <KpiCard
            label="Revenue"
            value="AED 489.2K"
            :delta="8.6"
            delta-period="vs last month"
            subtitle="Cost captured: 94%"
            :sparkline="[10, 15, 12, 18, 25, 22, 30, 38]"
            clickable
          />
          <KpiCard
            label="Late Trips"
            value="14"
            :delta="-22.5"
            good-direction="down"
            delta-period="vs prev"
            subtitle="Target < 20 trips"
            :sparkline="[40, 38, 32, 28, 22, 18, 16, 14]"
            clickable
          />
          <KpiCard
            label="Fleet Utilisation"
            value="87.4"
            unit="%"
            :delta="3.1"
            is-pts
            delta-period="vs prev"
            subtitle="Own trucks on road: 46"
            :sparkline="[70, 72, 75, 78, 80, 84, 86, 87]"
            clickable
          />
        </div>

        <Card class="p-6 flex flex-wrap items-center justify-between gap-6">
          <!-- Avatars & Groups -->
          <div class="flex items-center gap-4">
            <Avatar name="Rashid Khan" :size="40" />
            <Avatar name="Nitesh Vashisth" :size="32" />
            <AvatarGroup :overflow-count="4" :size="32">
              <Avatar name="John Doe" :size="32" />
              <Avatar name="Ali Al-Mansoor" :size="32" />
              <Avatar name="Carlos Silva" :size="32" />
            </AvatarGroup>
          </div>

          <!-- Micro-components -->
          <div class="flex items-center gap-4">
            <span class="text-xs text-secondary flex items-center gap-1 font-mono">
              <span>ORD-90241</span>
              <CopyButton text="ORD-90241" />
            </span>
            <Divider orientation="vertical" class="h-6" />
            <div class="flex items-center gap-1 text-xs">
              <span class="text-secondary">Shortcut:</span>
              <Kbd>⌘</Kbd><Kbd>K</Kbd>
            </div>
          </div>
        </Card>
      </section>

      <!-- 5. Navigation Primitives (Tabs, Stepper, Breadcrumbs, Pagination) -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold flex items-center gap-2">
          <span>🧭 Navigation (Tabs, Stepper, Breadcrumbs, Pagination)</span>
        </h2>
        <Card class="p-6 space-y-6">
          <Breadcrumbs
            :items="[
              { label: 'Operations', icon: Layers, to: '/dashboard' },
              { label: 'Orders', to: '/r/orders' },
              { label: 'ORD-2026-9041' },
            ]"
          />

          <Divider />

          <!-- Tabs Variants -->
          <div class="space-y-3">
            <span class="text-xs font-mono text-muted uppercase tracking-wider block">Tabs: Underline & Segmented</span>
            <Tabs v-model="activeTab" variant="underline" :tabs="mockTabs" />
            <Tabs v-model="activeSegment" variant="segmented" :tabs="[{ value: 'board', label: 'Kanban Board' }, { value: 'list', label: 'List View' }]" />
          </div>

          <Divider />

          <!-- Stepper -->
          <div class="space-y-3">
            <span class="text-xs font-mono text-muted uppercase tracking-wider block">Stepper Wizard</span>
            <Stepper
              :current-step="currentWizardStep"
              :max-visited-step="2"
              :steps="[
                { title: 'Order Details' },
                { title: 'Cargo & Vehicles' },
                { title: 'Route Scheduling', hasError: true },
                { title: 'Pricing & Review' },
              ]"
              @step-click="currentWizardStep = $event"
            />
          </div>

          <Divider />

          <!-- Pagination -->
          <Pagination
            :page="page"
            :page-size="20"
            :total="1284"
            @update:page="page = $event"
          />
        </Card>
      </section>

      <!-- 6. Overlays, Dialogs & Feedback -->
      <section class="space-y-4">
        <h2 class="text-lg font-semibold flex items-center gap-2">
          <span>🪟 Overlays, Drawers & Toast Notifications</span>
        </h2>
        <Card class="p-6 space-y-6">
          <div class="flex flex-wrap items-center gap-3">
            <Button variant="primary" @click="showModal = true">Open Modal</Button>
            <Button variant="secondary" @click="showDrawer = true">Open Slide-Over Drawer</Button>
            <Button variant="danger" @click="testConfirm">Test Destructive Confirm</Button>
            <Button variant="ghost" @click="testToasts">Trigger Toasts</Button>

            <DropdownMenu
              :items="[
                { header: 'Order Actions' },
                { label: 'View Details', icon: Eye, action: () => toast.info('Navigating to detail') },
                { label: 'Edit Leg Allocation', icon: Edit, action: () => toast.info('Opening edit mode') },
                { separator: true },
                { label: 'Cancel Order', icon: Trash2, danger: true, action: () => testConfirm() },
              ]"
            >
              <template #trigger>
                <Button variant="outline" :trailing-icon="ChevronDown">Actions Menu</Button>
              </template>
            </DropdownMenu>
          </div>

          <Divider />

          <!-- Skeletons Demo -->
          <div class="space-y-2">
            <span class="text-xs font-mono text-muted uppercase tracking-wider block">Skeletons</span>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Skeleton variant="card" />
              <div class="card p-4 space-y-3">
                <Skeleton size="md" width="w-3/4" />
                <Skeleton size="sm" width="w-full" />
                <Skeleton size="sm" width="w-1/2" />
              </div>
              <div class="card p-4 flex items-center gap-3">
                <Skeleton variant="avatar" :size="40" />
                <div class="flex-1 space-y-2">
                  <Skeleton size="sm" width="w-24" />
                  <Skeleton size="sm" width="w-36" />
                </div>
              </div>
            </div>
          </div>

          <Divider />

          <!-- Empty State Demo -->
          <EmptyState
            variant="no-results"
            action-text="Reset All Filters"
            secondary-text="Browse All Orders"
            @action="toast.success('Filters cleared')"
          />
        </Card>
      </section>

      <!-- Modal Preview -->
      <Modal v-model:open="showModal" title="Trip Allocation Cockpit" description="Assign vehicle, driver, and trailer to Leg #1">
        <div class="space-y-4 text-sm">
          <FormField label="Assigned Driver" required>
            <Combobox v-model="form.driverId" :options="mockDrivers" placeholder="Select active driver…" />
          </FormField>
          <FormField label="Vehicle Plate Number" required>
            <Combobox v-model="form.vehicleId" :options="mockVehicles" placeholder="Select fleet vehicle…" />
          </FormField>
        </div>
        <template #footer>
          <Button variant="ghost" @click="showModal = false">Cancel</Button>
          <Button variant="primary" @click="showModal = false; toast.success('Trip allocated successfully')">Confirm Allocation</Button>
        </template>
      </Modal>

      <!-- 10. DataTable & Registry Cells Showcase -->
      <section class="space-y-4">
        <div class="flex items-center justify-between">
          <h2 class="text-lg font-semibold flex items-center gap-2">
            <span>📊 Phase 4: TanStack DataTable & Cell Formatters</span>
          </h2>
          <div class="flex items-center gap-2">
            <span class="text-xs text-secondary">Density:</span>
            <div role="radiogroup" aria-label="Table density" class="inline-flex rounded-lg border border-border-default bg-surface p-0.5 text-xs">
              <button
                v-for="d in ['compact', 'normal', 'relaxed']"
                :key="d"
                type="button"
                role="radio"
                :aria-checked="tableDensity === d"
                :class="[
                  'px-2.5 py-1 rounded-md capitalize transition-colors focus-ring cursor-pointer',
                  tableDensity === d ? 'bg-primary-600 text-white font-medium' : 'text-secondary hover:text-primary'
                ]"
                @click="tableDensity = d"
              >
                {{ d }}
              </button>
            </div>
          </div>
        </div>

        <div class="w-full min-w-0 max-w-full overflow-hidden">
          <div class="flex items-center justify-between text-[11px] text-muted pb-1.5 sm:hidden">
            <span>⇄ Swipe horizontally to see all columns</span>
          </div>
          <DataTable
            :rows="mockOrders"
            :columns="mockOrderColumns"
            :fields="mockOrderFields"
            resource-key="orders"
            resource-title="Orders"
            :density="tableDensity"
            :ordering="tableOrdering"
            :selected-row-ids="tableSelectedIds"
            :is-page-selected="tableSelectedIds.length === mockOrders.length"
            :is-page-partially-selected="tableSelectedIds.length > 0 && tableSelectedIds.length < mockOrders.length"
            @sort="tableOrdering = tableOrdering === $event ? '-' + $event : $event"
            @toggle-select="toggleTableSelect"
            @select-all="toggleTableSelectAll"
            @row-click="openQuickView"
          />
        </div>

        <DataTableBulkBar
          :selected-count="tableSelectedIds.length"
          :total-count="mockOrders.length"
          @clear="tableSelectedIds = []"
          @export-selected="toast.success(`Exporting ${tableSelectedIds.length} orders`)"
        />
      </section>

      <!-- Drawer Preview -->
      <Drawer
        v-model:open="showDrawer"
        :title="`Quick View: ${activeOrder.number}`"
        description="Live trip status, cargo summary, and timeline"
        width="md"
      >
        <div class="space-y-6 text-sm">
          <div class="flex items-center justify-between pb-3 border-b border-border-default">
            <div>
              <div class="font-mono text-xs text-secondary">{{ activeOrder.lane }}</div>
              <div class="text-base font-bold mt-0.5">{{ activeOrder.customer_label }}</div>
            </div>
            <StatusPill :status="activeOrder.status" :label="activeOrder.status_label" show-icon />
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div class="card p-3">
              <span class="text-xs text-muted">Planned Pickup</span>
              <div class="font-medium text-xs mt-1">{{ formatDateTime(activeOrder.loading_at) }}</div>
            </div>
            <div class="card p-3">
              <span class="text-xs text-muted">Sell Rate</span>
              <div class="font-medium text-xs mt-1 font-mono text-primary-600 dark:text-primary-400">
                {{ formatCurrency(activeOrder.sell_rate, activeOrder.currency) }}
              </div>
            </div>
            <div class="card p-3">
              <span class="text-xs text-muted">Cargo Payload</span>
              <div class="font-medium text-xs mt-1">{{ formatWeight(activeOrder.weight_t) }}</div>
            </div>
            <div class="card p-3">
              <span class="text-xs text-muted">ETA Destination</span>
              <div class="font-medium text-xs mt-1 text-emerald-600 dark:text-emerald-400">On Track · Active</div>
            </div>
          </div>
        </div>
        <template #footer>
          <Button variant="ghost" @click="showDrawer = false">Close</Button>
          <Button variant="primary" @click="showDrawer = false; toast.info(`Navigating to ${activeOrder.number}`)">Open Full Page ↗</Button>
        </template>
      </Drawer>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import {
  Sun, Moon, Monitor, Plus, ArrowRight, Settings, Eye, Edit, Trash2,
  ChevronDown, Layers
} from 'lucide-vue-next'
import { useTheme } from '../composables/useTheme'
import { useToast } from '../composables/useToast'
import { useConfirm } from '../composables/useConfirm'

import { formatDateTime, formatCurrency, formatWeight } from '../utils/format'
import Button from '../components/ui/Button.vue'
import Input from '../components/ui/Input.vue'
import Textarea from '../components/ui/Textarea.vue'
import FormField from '../components/ui/FormField.vue'
import Select from '../components/ui/Select.vue'
import Combobox from '../components/ui/Combobox.vue'
import MultiSelect from '../components/ui/MultiSelect.vue'
import DatePicker from '../components/ui/DatePicker.vue'
import DateRangePicker from '../components/ui/DateRangePicker.vue'
import Checkbox from '../components/ui/Checkbox.vue'
import Switch from '../components/ui/Switch.vue'
import RadioGroup from '../components/ui/RadioGroup.vue'
import Badge from '../components/ui/Badge.vue'
import StatusPill from '../components/ui/StatusPill.vue'
import Avatar from '../components/ui/Avatar.vue'
import AvatarGroup from '../components/ui/AvatarGroup.vue'
import Card from '../components/ui/Card.vue'
import Tabs from '../components/ui/Tabs.vue'
import Tooltip from '../components/ui/Tooltip.vue'
import DropdownMenu from '../components/ui/DropdownMenu.vue'
import Modal from '../components/ui/Modal.vue'
import Drawer from '../components/ui/Drawer.vue'
import ConfirmDialog from '../components/ui/ConfirmDialog.vue'
import Stepper from '../components/ui/Stepper.vue'
import Breadcrumbs from '../components/ui/Breadcrumbs.vue'
import Pagination from '../components/ui/Pagination.vue'
import KpiCard from '../components/ui/KpiCard.vue'
import Kbd from '../components/ui/Kbd.vue'
import Divider from '../components/ui/Divider.vue'
import CopyButton from '../components/ui/CopyButton.vue'
import Skeleton from '../components/feedback/Skeleton.vue'
import EmptyState from '../components/feedback/EmptyState.vue'
import ToastContainer from '../components/feedback/ToastContainer.vue'
import DataTable from '../components/data-table/DataTable.vue'
import DataTableBulkBar from '../components/data-table/DataTableBulkBar.vue'

const { theme, setTheme } = useTheme()
const toast = useToast()
const { confirm } = useConfirm()

function modeIcon(mode) {
  if (mode === 'light') return Sun
  if (mode === 'dark') return Moon
  return Monitor
}

const showModal = ref(false)
const showDrawer = ref(false)
const page = ref(1)
const activeTab = ref('overview')
const activeSegment = ref('board')
const currentWizardStep = ref(1)

const form = reactive({
  weight: 24.5,
  rate: '1850.00',
  password: '',
  serviceType: 'FTL',
  customerId: 1,
  docTypes: [1, 2],
  loadingDate: '2026-10-20T08:30:00Z',
  startDate: '2026-10-01',
  endDate: '2026-10-20',
  notes: 'Fragile industrial coils. Secure with heavy-duty chains.',
  isHazardous: false,
  autoDispatch: true,
  billingType: 'per_trip',
  driverId: null,
  vehicleId: null,
})

const mockCustomers = [
  { id: 1, name: 'Emirates Steel LLC', code: 'CUST-001' },
  { id: 2, name: 'DP World Logistics', code: 'CUST-002' },
  { id: 3, name: 'Al Ghurair Foods', code: 'CUST-003' },
  { id: 4, name: 'Gulf Petrochem', code: 'CUST-004' },
]

const mockDrivers = [
  { id: 1, display: 'Rashid Khan (DRV-102)' },
  { id: 2, display: 'Muhammad Tariq (DRV-108)' },
  { id: 3, display: 'Rajesh Kumar (DRV-114)' },
]

const mockVehicles = [
  { id: 1, display: 'DXB-55912 (Mercedes Actros)' },
  { id: 2, display: 'AUH-88231 (Volvo FH16)' },
  { id: 3, display: 'SHJ-12093 (Scania R500)' },
]

const mockDocs = [
  { id: 1, name: 'Commercial Invoice' },
  { id: 2, name: 'Proof of Delivery (POD)' },
  { id: 3, name: 'Dangerous Goods Declaration' },
  { id: 4, name: 'Customs Clearance Exit Bill' },
]

const mockTabs = [
  { value: 'overview', label: 'Overview' },
  { value: 'trips', label: 'Legs & Trips', count: 3 },
  { value: 'documents', label: 'Documents', count: 4 },
  { value: 'billing', label: 'Invoices & Billing', count: 1 },
  { value: 'audit', label: 'Audit Trail' },
]

async function testConfirm() {
  const ok = await confirm({
    title: 'Delete Order Record',
    message: 'This action will revoke all associated trip legs and vendor orders.',
    confirmText: 'Delete Order',
    danger: true,
    requireMatch: 'ORD-9041',
  })
  if (ok) {
    toast.error('Order ORD-9041 deleted.')
  } else {
    toast.info('Deletion cancelled.')
  }
}

function testToasts() {
  toast.success('Order ORD-2026-9041 confirmed successfully.')
  setTimeout(() => {
    toast.warning('Vehicle DXB-55912 requires oil service in 500 km.')
  }, 300)
}

// DataTable Showcase State & Data
const mockOrderColumns = [
  { name: 'number', label: 'Order #' },
  { name: 'customer', label: 'Customer' },
  { name: 'lane', label: 'Lane' },
  { name: 'loading_at', label: 'Loading At' },
  { name: 'status', label: 'Status' },
  { name: 'sell_rate', label: 'Sell Rate', align: 'right' },
  { name: 'weight_t', label: 'Weight', align: 'right' },
]

const mockOrderFields = {
  number: { type: 'str', label: 'Order #' },
  customer: { type: 'fk', label: 'Customer', resource: 'customers' },
  lane: { type: 'str', label: 'Lane' },
  loading_at: { type: 'datetime', label: 'Loading At' },
  status: { type: 'choice', label: 'Status' },
  sell_rate: { type: 'decimal', money: true, label: 'Sell Rate' },
  weight_t: { type: 'float', label: 'Weight' },
}

const mockOrders = [
  {
    id: 1,
    number: 'ORD-2026-9041',
    customer: 1,
    customer_label: 'Emirates Steel LLC',
    lane: 'DXB → AUH',
    loading_at: '2026-10-20T08:30:00Z',
    status: 'in_transit',
    status_label: 'In transit',
    sell_rate: '2450.00',
    currency: 'AED',
    weight_t: 26.4,
  },
  {
    id: 2,
    number: 'ORD-2026-9042',
    customer: 2,
    customer_label: 'DP World Logistics',
    lane: 'JAFZA → DWC',
    loading_at: '2026-10-20T10:00:00Z',
    status: 'confirmed',
    status_label: 'Confirmed',
    sell_rate: '1850.00',
    currency: 'AED',
    weight_t: 18.0,
  },
  {
    id: 3,
    number: 'ORD-2026-9043',
    customer: 3,
    customer_label: 'Al Ghurair Foods',
    lane: 'SHJ → RAK',
    loading_at: '2026-10-19T14:15:00Z',
    status: 'delivered',
    status_label: 'Delivered',
    sell_rate: '3100.00',
    currency: 'AED',
    weight_t: 31.2,
  },
  {
    id: 4,
    number: 'ORD-2026-9044',
    customer: 4,
    customer_label: 'Gulf Petrochem',
    lane: 'FUJ → DXB',
    loading_at: '2026-10-21T06:00:00Z',
    status: 'pending',
    status_label: 'Pending',
    sell_rate: '2200.00',
    currency: 'AED',
    weight_t: 22.5,
  },
]

const tableDensity = ref('normal')
const tableOrdering = ref('loading_at')
const tableSelectedIds = ref([])
const activeOrder = ref(mockOrders[0])

function toggleTableSelect(id) {
  if (tableSelectedIds.value.includes(id)) {
    tableSelectedIds.value = tableSelectedIds.value.filter((i) => i !== id)
  } else {
    tableSelectedIds.value = [...tableSelectedIds.value, id]
  }
}

function toggleTableSelectAll(checked) {
  tableSelectedIds.value = checked ? mockOrders.map((o) => o.id) : []
}

function openQuickView(row) {
  activeOrder.value = row || mockOrders[0]
  showDrawer.value = true
}
</script>
