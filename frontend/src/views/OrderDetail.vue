<template>
  <!-- Error / 404 State -->
  <div v-if="error" class="mx-auto w-full max-w-6xl py-12 text-center">
    <EmptyState
      title="Order Not Found"
      :description="error"
      action-label="Back to Orders"
      @action="$router.push('/r/orders')"
    />
  </div>

  <!-- Loading Skeletons -->
  <div v-else-if="loading || !order" class="mx-auto w-full max-w-7xl space-y-6">
    <div class="h-6 w-32 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
    <div class="flex justify-between items-center">
      <div class="h-10 w-72 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
      <div class="h-10 w-48 bg-slate-200 dark:bg-slate-800 rounded animate-pulse" />
    </div>
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2 space-y-6">
        <div class="h-44 bg-slate-100 dark:bg-slate-900 rounded-xl animate-pulse" />
        <div class="h-72 bg-slate-100 dark:bg-slate-900 rounded-xl animate-pulse" />
      </div>
      <div class="space-y-6">
        <div class="h-60 bg-slate-100 dark:bg-slate-900 rounded-xl animate-pulse" />
        <div class="h-48 bg-slate-100 dark:bg-slate-900 rounded-xl animate-pulse" />
      </div>
    </div>
  </div>

  <!-- Main Order Detail -->
  <div v-else class="mx-auto w-full max-w-7xl space-y-6">
    <!-- Breadcrumb -->
    <div class="flex items-center justify-between">
      <router-link
        to="/r/orders"
        class="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 dark:hover:text-white transition-colors"
      >
        <ArrowLeft class="w-4 h-4" />
        <span>Back to Orders</span>
      </router-link>

      <!-- Record Navigation Links -->
      <div class="flex items-center gap-1 text-xs text-slate-400">
        <span class="font-mono">Order Details</span>
      </div>
    </div>

    <!-- Header Banner -->
    <div class="p-6 rounded-2xl border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-xs space-y-4">
      <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <!-- Title & Status -->
        <div class="space-y-1.5">
          <div class="flex flex-wrap items-center gap-2.5">
            <span class="text-2xl">📦</span>
            <h1 class="text-2xl font-bold tracking-tight text-slate-900 dark:text-slate-100 font-mono">
              {{ order.number }}
            </h1>
            <CopyButton :text="order.number" />
            <StatusPill
              :status="order.status"
              :label="order.status_label"
              size="md"
            />
            <span v-if="order.job_type" class="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
              {{ order.job_type }}
            </span>
          </div>

          <!-- Subtitle Key Metadata Row -->
          <div class="flex flex-wrap items-center gap-x-4 gap-y-1 text-xs text-slate-500 dark:text-slate-400">
            <span class="font-medium text-slate-900 dark:text-slate-100">
              🏢 {{ order.customer_label }}
            </span>
            <span>•</span>
            <span>📍 {{ order.lane_label }}</span>
            <span v-if="order.branch_label">•</span>
            <span v-if="order.branch_label">🏛 {{ order.branch_label }}</span>
            <span>•</span>
            <span>📅 {{ formatDate(order.order_date) }}</span>
          </div>
        </div>

        <!-- Action Buttons -->
        <div class="flex flex-wrap items-center gap-2">
          <!-- Status Transition Buttons -->
          <template v-for="s in order.next_statuses" :key="s.value">
            <Button
              :variant="['cancelled', 'rejected'].includes(s.value) ? 'danger-ghost' : 'primary'"
              size="sm"
              :loading="transitionBusy"
              @click="moveStatus(s.value)"
            >
              <span>{{ s.label }}</span>
              <ArrowRight class="w-3.5 h-3.5 ml-1" />
            </Button>
          </template>

          <!-- Edit Button -->
          <router-link :to="`/r/orders/${order.id}/edit`">
            <Button variant="outline" size="sm">
              <Pencil class="w-3.5 h-3.5 mr-1.5" />
              <span>Edit</span>
            </Button>
          </router-link>

          <!-- Secondary Actions Kebab -->
          <DropdownMenu :items="secondaryMenuItems" align="end">
            <template #trigger>
              <button
                type="button"
                class="inline-flex items-center justify-center h-8 w-8 rounded-lg border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 hover:bg-slate-50 dark:hover:bg-slate-800 text-slate-600 dark:text-slate-300 transition-colors shadow-xs"
                title="More Actions"
              >
                <MoreVertical class="w-4 h-4" />
              </button>
            </template>
          </DropdownMenu>
        </div>
      </div>

      <!-- Financial Snapshot Strip -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-3 border-t border-slate-100 dark:border-slate-800 text-xs">
        <div>
          <span class="text-[11px] text-slate-400 block">Sell Rate</span>
          <span class="text-sm font-bold text-slate-900 dark:text-slate-100 font-mono">
            {{ formatCurrency(order.sell_rate, order.currency) }}
          </span>
        </div>
        <div>
          <span class="text-[11px] text-slate-400 block">Trip Cost (Legs)</span>
          <span class="text-sm font-bold text-slate-900 dark:text-slate-100 font-mono">
            {{ formatCurrency(order.cost, order.currency) }}
          </span>
        </div>
        <div>
          <span class="text-[11px] text-slate-400 block">Gross Margin</span>
          <span :class="['text-sm font-bold font-mono', Number(order.margin) >= 0 ? 'text-emerald-600 dark:text-emerald-400' : 'text-rose-600']">
            {{ formatCurrency(order.margin, order.currency) }}
          </span>
        </div>
        <div>
          <span class="text-[11px] text-slate-400 block">Committed Fleet</span>
          <span class="text-sm font-bold text-slate-900 dark:text-slate-100 font-mono">
            {{ order.vehicles_committed }} of {{ order.num_vehicles }} vehicles
          </span>
        </div>
      </div>
    </div>

    <!-- URL-Synced Navigation Tabs -->
    <Tabs
      v-model="activeTab"
      :tabs="detailTabs"
      class="border-b border-slate-200 dark:border-slate-800"
    />

    <!-- TAB 1: OVERVIEW -->
    <div v-if="activeTab === 'overview'" class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Main Left Column -->
      <div class="lg:col-span-2 space-y-6">
        <!-- Milestone Progress Tracker -->
        <StatusTracker
          :current-status="order.status"
          :delay-minutes="totalDelayMinutes"
          :timestamps="{
            pending: order.created_at,
            confirmed: order.loading_at,
            active: order.trips?.[0]?.planned_start,
            completed: order.trips?.[order.trips.length - 1]?.actual_end
          }"
        />

        <!-- Route & Map Corridor -->
        <RouteMap
          :source="order.lane_detail?.source"
          :destination="order.lane_detail?.destination"
          :via="order.lane_detail?.via"
          :distance-km="order.lane_detail?.distance_km"
          :service-type="order.lane_detail?.service_type"
          :pickup-address="order.pickup_address"
          :pickup-contact="order.pickup_contact"
          :load-cutoff="order.load_cutoff"
          :drop-address="order.drop_address"
          :drop-contact="order.drop_contact"
          :offload-cutoff="order.offload_cutoff"
        />

        <!-- Cargo & Specifications Card -->
        <Card class="p-5 space-y-4">
          <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
            <h3 class="text-sm font-semibold text-slate-900 dark:text-slate-100">Cargo & Packaging</h3>
            <div class="flex items-center gap-1.5">
              <span v-if="order.temperature_controlled" class="px-2 py-0.5 rounded text-[10px] font-semibold bg-sky-50 text-sky-700 dark:bg-sky-950/60 dark:text-sky-300">
                ❄ Cold Chain
              </span>
              <span v-if="order.hazardous" class="px-2 py-0.5 rounded text-[10px] font-semibold bg-rose-50 text-rose-700 dark:bg-rose-950/60 dark:text-rose-300">
                ☣ Hazardous
              </span>
              <span v-if="order.stackable" class="px-2 py-0.5 rounded text-[10px] font-semibold bg-slate-100 text-slate-700 dark:bg-slate-800 dark:text-slate-300">
                Stackable
              </span>
            </div>
          </div>

          <dl class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div>
              <dt class="text-slate-400">Product / Charge Code</dt>
              <dd class="mt-0.5 font-semibold text-slate-800 dark:text-slate-200">{{ order.product_label || '—' }}</dd>
            </div>
            <div>
              <dt class="text-slate-400">Container Type</dt>
              <dd class="mt-0.5 font-semibold text-slate-800 dark:text-slate-200">{{ order.container_type_label || 'Standard Trailer' }}</dd>
            </div>
            <div>
              <dt class="text-slate-400">Commodity</dt>
              <dd class="mt-0.5 font-semibold text-slate-800 dark:text-slate-200">{{ order.commodity || 'General Cargo' }}</dd>
            </div>
            <div>
              <dt class="text-slate-400">Weight & Quantity</dt>
              <dd class="mt-0.5 font-semibold text-slate-800 dark:text-slate-200 font-mono">
                {{ order.weight_t ? `${order.weight_t} t` : '—' }} ({{ order.quantity || 1 }} unit)
              </dd>
            </div>
          </dl>
        </Card>
      </div>

      <!-- Right Sidebar Column -->
      <div class="space-y-6">
        <!-- Allocation Summary Component -->
        <AllocationSummary
          :vehicles-committed="order.vehicles_committed"
          :num-vehicles="order.num_vehicles"
          :allocation-status="order.allocation_status"
          :driver-name="primaryTrip?.driver_label"
          :vehicle-plate="primaryTrip?.vehicle_label || (primaryTrip?.vendor_label ? 'Market: ' + primaryTrip.vendor_label : null)"
          :weight-t="order.weight_t"
        />

        <!-- Commercial & Contracting -->
        <Card class="p-5 space-y-3 text-xs">
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">
            Commercial References
          </h3>
          <div class="space-y-2">
            <div class="flex justify-between">
              <span class="text-slate-400">Customer Reference:</span>
              <span class="font-mono font-medium text-slate-800 dark:text-slate-200">{{ order.reference || '—' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Shipment Ref:</span>
              <span class="font-mono font-medium text-slate-800 dark:text-slate-200">{{ order.shipment_reference || '—' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Contract:</span>
              <span class="font-medium text-slate-800 dark:text-slate-200">{{ order.contract_label || 'Ad-hoc Spot' }}</span>
            </div>
            <div class="flex justify-between">
              <span class="text-slate-400">Fulfillment Vendor:</span>
              <span class="font-medium text-slate-800 dark:text-slate-200">{{ order.vendor_label || 'In-house Fleet' }}</span>
            </div>
          </div>
        </Card>

        <!-- Audit & Creator Meta -->
        <Card class="p-5 space-y-2 text-xs">
          <h3 class="text-xs font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 border-b border-slate-100 dark:border-slate-800 pb-2">
            Audit Trail
          </h3>
          <div class="space-y-1.5 text-slate-500 dark:text-slate-400 text-[11px]">
            <p>Created: <span class="text-slate-800 dark:text-slate-200 font-medium">{{ formatDateTime(order.created_at) }}</span> by {{ order.created_by || 'Admin' }}</p>
            <p>Updated: <span class="text-slate-800 dark:text-slate-200 font-medium">{{ formatDateTime(order.updated_at) }}</span></p>
            <p v-if="order.notes" class="pt-2 italic border-t border-slate-100 dark:border-slate-800 text-slate-700 dark:text-slate-300">
              "{{ order.notes }}"
            </p>
          </div>
        </Card>
      </div>
    </div>

    <!-- TAB 2: LEGS & TRIPS -->
    <div v-else-if="activeTab === 'trips'" class="space-y-4">
      <Card class="overflow-hidden">
        <div class="flex items-center justify-between p-4 border-b border-slate-100 dark:border-slate-800">
          <div>
            <h3 class="text-sm font-semibold text-slate-900 dark:text-slate-100">Scheduled Legs & Executing Trips</h3>
            <p class="text-xs text-slate-500">Each leg represents an individual vehicle assignment on the route corridor.</p>
          </div>
          <router-link :to="`/r/trips/new`">
            <Button variant="primary" size="sm">
              <Plus class="w-4 h-4 mr-1" />
              <span>Add Leg</span>
            </Button>
          </router-link>
        </div>

        <div class="overflow-x-auto">
          <table class="w-full text-left text-xs border-collapse">
            <thead class="bg-slate-50 dark:bg-slate-800/60 text-[11px] font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-200 dark:border-slate-800">
              <tr>
                <th class="px-4 py-3">Trip Number</th>
                <th class="px-4 py-3">Leg</th>
                <th class="px-4 py-3">Status</th>
                <th class="px-4 py-3">Vehicle</th>
                <th class="px-4 py-3">Driver</th>
                <th class="px-4 py-3">Planned Start</th>
                <th class="px-4 py-3">Delay</th>
                <th class="px-4 py-3 text-right">Buy Rate</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-100 dark:divide-slate-800/60">
              <tr
                v-for="t in order.trips"
                :key="t.id"
                class="hover:bg-slate-50 dark:hover:bg-slate-800/50 cursor-pointer transition-colors"
                @click="$router.push(`/r/trips/${t.id}`)"
              >
                <td class="px-4 py-3 font-mono font-semibold text-slate-900 dark:text-slate-100">
                  {{ t.number }}
                </td>
                <td class="px-4 py-3 font-semibold">{{ t.leg_no }}</td>
                <td class="px-4 py-3">
                  <StatusPill :status="t.status" :label="t.status_label" size="sm" />
                </td>
                <td class="px-4 py-3 font-mono text-slate-700 dark:text-slate-300">
                  {{ t.vehicle_label || (t.vendor_label ? 'Market: ' + t.vendor_label : '—') }}
                </td>
                <td class="px-4 py-3 font-medium">
                  {{ t.driver_label || '—' }}
                </td>
                <td class="px-4 py-3 text-slate-500 font-mono">
                  {{ formatDateTime(t.planned_start) }}
                </td>
                <td class="px-4 py-3">
                  <span v-if="t.delay_minutes" class="text-rose-600 font-semibold">
                    +{{ t.delay_minutes }}m
                  </span>
                  <span v-else class="text-emerald-600 font-medium">On time</span>
                </td>
                <td class="px-4 py-3 text-right font-mono font-bold text-slate-900 dark:text-slate-100">
                  {{ formatCurrency(t.buy_rate, order.currency) }}
                </td>
              </tr>
              <tr v-if="!order.trips?.length">
                <td colspan="8" class="p-8 text-center text-slate-400">
                  No leg trips have been generated yet. Confirming the order will auto-create one leg per vehicle.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </Card>
    </div>

    <!-- TAB 3: DOCUMENTS -->
    <div v-else-if="activeTab === 'documents'" class="space-y-4">
      <Card class="p-6">
        <div class="flex items-center justify-between pb-4 border-b border-slate-100 dark:border-slate-800">
          <div>
            <h3 class="text-sm font-semibold text-slate-900 dark:text-slate-100">Attached Shipping Documents</h3>
            <p class="text-xs text-slate-500">Commercial invoices, e-PODs, and customs clearance certificates.</p>
          </div>
          <Button variant="outline" size="sm">
            <Upload class="w-4 h-4 mr-1.5" />
            <span>Upload Document</span>
          </Button>
        </div>

        <div class="py-12 text-center text-xs text-slate-400 space-y-2">
          <FileText class="w-8 h-8 mx-auto text-slate-300 dark:text-slate-600" />
          <p>No external documents attached to this order record yet.</p>
        </div>
      </Card>
    </div>

    <!-- TAB 4: BILLING & INVOICES -->
    <div v-else-if="activeTab === 'billing'" class="space-y-4">
      <Card class="p-5 space-y-4">
        <div class="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 pb-3">
          <div>
            <h3 class="text-sm font-semibold text-slate-900 dark:text-slate-100">Invoices & Receivables</h3>
            <p class="text-xs text-slate-500">Customer billing statements generated for this fulfillment.</p>
          </div>
          <router-link :to="`/r/invoices/new`">
            <Button variant="primary" size="sm">
              <Plus class="w-4 h-4 mr-1" />
              <span>Generate Invoice</span>
            </Button>
          </router-link>
        </div>

        <div v-if="order.invoices?.length" class="space-y-2">
          <div
            v-for="i in order.invoices"
            :key="i.id"
            class="flex items-center justify-between p-3 rounded-lg border border-slate-200 dark:border-slate-800 bg-slate-50 dark:bg-slate-800/40 text-xs"
          >
            <div class="flex items-center gap-3">
              <Receipt class="w-4 h-4 text-brand-600" />
              <div>
                <router-link :to="`/r/invoices/${i.id}`" class="font-mono font-bold text-brand-600 dark:text-brand-400 hover:underline">
                  #{{ i.number }}
                </router-link>
                <span class="text-slate-400 ml-2">Total: {{ formatCurrency(i.total, order.currency) }}</span>
              </div>
            </div>
            <StatusPill :status="i.status" size="sm" />
          </div>
        </div>
        <div v-else class="py-8 text-center text-xs text-slate-400">
          No customer invoices have been issued yet.
        </div>
      </Card>
    </div>

    <!-- TAB 5: ACTIVITY -->
    <div v-else-if="activeTab === 'activity'" class="space-y-4">
      <ActivityTimeline
        :items="activityItems"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft,
  ArrowRight,
  Pencil,
  Plus,
  MoreVertical,
  Upload,
  FileText,
  Receipt,
  Copy,
  Trash2,
  Share2,
} from 'lucide-vue-next'
import api, { errText } from '../api'
import { formatDate, formatDateTime, formatCurrency } from '../utils/format'
import { useToast } from '../composables/useToast'
import { useConfirm } from '../composables/useConfirm'

import Card from '../components/ui/Card.vue'
import Button from '../components/ui/Button.vue'
import Tabs from '../components/ui/Tabs.vue'
import StatusPill from '../components/ui/StatusPill.vue'
import CopyButton from '../components/ui/CopyButton.vue'
import DropdownMenu from '../components/ui/DropdownMenu.vue'
import EmptyState from '../components/feedback/EmptyState.vue'
import RouteMap from '../components/detail/RouteMap.vue'
import StatusTracker from '../components/detail/StatusTracker.vue'
import AllocationSummary from '../components/detail/AllocationSummary.vue'
import ActivityTimeline from '../components/detail/ActivityTimeline.vue'

const route = useRoute()
const router = useRouter()
const toast = useToast()
const confirm = useConfirm()

const orderId = computed(() => route.params.id)
const order = ref(null)
const loading = ref(true)
const error = ref('')
const transitionBusy = ref(false)

// URL-Synced Tabs
const activeTab = ref(route.query.tab || 'overview')
watch(activeTab, (t) => {
  router.replace({ query: { ...route.query, tab: t === 'overview' ? undefined : t } }).catch(() => {})
})

const detailTabs = computed(() => {
  return [
    { value: 'overview', label: 'Overview' },
    { value: 'trips', label: 'Legs & Trips', count: order.value?.trips?.length || 0 },
    { value: 'documents', label: 'Documents' },
    { value: 'billing', label: 'Billing', count: order.value?.invoices?.length || 0 },
    { value: 'activity', label: 'Activity' },
  ]
})

const primaryTrip = computed(() => order.value?.trips?.[0] || null)

const totalDelayMinutes = computed(() => {
  if (!order.value?.trips) return 0
  return order.value.trips.reduce((acc, t) => acc + (t.delay_minutes || 0), 0)
})

const activityItems = computed(() => {
  if (!order.value) return []
  const items = [
    {
      id: 'evt_created',
      title: 'Order Created',
      description: `Order #${order.value.number} placed for ${order.value.customer_label}`,
      timestamp: order.value.created_at,
      actor: order.value.created_by || 'Operations',
      tone: 'success',
    },
  ]
  if (order.value.updated_at && order.value.updated_at !== order.value.created_at) {
    items.push({
      id: 'evt_updated',
      title: 'Order Updated',
      description: `Status current: ${order.value.status_label}`,
      timestamp: order.value.updated_at,
      actor: 'System',
      tone: 'info',
    })
  }
  return items
})

const secondaryMenuItems = computed(() => {
  return [
    {
      label: 'Duplicate order',
      icon: Copy,
      action: () => {
        router.push({ path: '/r/orders/new', query: { duplicate_from: order.value.id } })
      },
    },
    {
      label: 'Share link',
      icon: Share2,
      action: () => {
        navigator.clipboard?.writeText(window.location.href)
        toast.success('Direct link copied to clipboard')
      },
    },
    { separator: true },
    {
      label: 'Cancel order',
      icon: Trash2,
      danger: true,
      action: async () => {
        const ok = await confirm.danger({
          title: 'Cancel Order?',
          message: 'Are you sure you want to cancel this order? Associated trip allocations will be invalidated.',
          confirmText: 'Cancel order',
        })
        if (ok) {
          moveStatus('cancelled')
        }
      },
    },
  ]
})

async function loadOrder() {
  loading.value = true
  error.value = ''
  try {
    const res = await api.get(`orders/${orderId.value}/full/`)
    order.value = res.data
  } catch (e) {
    if (e.response?.status === 404) {
      error.value = 'Order record not found or access denied.'
    } else {
      error.value = errText(e)
    }
  } finally {
    loading.value = false
  }
}

async function moveStatus(nextStatus) {
  transitionBusy.value = true
  try {
    const res = await api.post(`orders/${order.value.id}/transition/`, { status: nextStatus })
    order.value = res.data
    toast.success(`Order transitioned to ${order.value.status_label}`)
  } catch (e) {
    toast.error(`Transition failed: ${errText(e)}`)
  } finally {
    transitionBusy.value = false
  }
}

watch(orderId, () => {
  loadOrder()
})

onMounted(() => {
  loadOrder()
})
</script>
