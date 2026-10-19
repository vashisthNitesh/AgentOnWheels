import {
  Package, Calendar, Key, Handshake, DollarSign, Mail, Gavel, MailCheck,
  HelpCircle, Search, FileSpreadsheet, FileText, Building2, Truck, UserCheck,
  Clock, Container, Disc, ArrowLeftRight, Wrench, ClipboardList, Box,
  ShieldAlert, Receipt, Inbox, Banknote, CreditCard, BarChart3, Settings,
  MapPin, Flag, Percent, GitFork, Fuel, Sliders, Users, Layers, LayoutDashboard,
  Navigation
} from 'lucide-vue-next'

const MODULE_ICONS = {
  // Navigation & Core
  dashboard: LayoutDashboard,
  'control-tower': Navigation,
  configuration: Settings,

  // Operations
  orders: Package,
  trips: Calendar,
  'lease-orders': Key,
  'vendor-orders': Handshake,

  // Rates & Commercial
  rates: DollarSign,
  rfqs: Mail,
  bids: Gavel,
  'bid-responses': MailCheck,
  'rate-inquiries': HelpCircle,
  sourcing: Search,
  quotations: FileSpreadsheet,
  'customer-contracts': FileText,
  'vendor-contracts': FileText,

  // Partners
  customers: Building2,
  vendors: Truck,

  // Fleet
  drivers: UserCheck,
  attendance: Clock,
  vehicles: Truck,
  trailers: Container,
  tyres: Disc,
  'asset-transfers': ArrowLeftRight,
  documents: FileText,

  // Workshop
  maintenance: Wrench,
  'job-cards': ClipboardList,
  'material-requests': Box,
  'gate-passes': ShieldAlert,

  // Finance
  invoices: Receipt,
  'vendor-invoices': Inbox,
  allowances: Banknote,
  payouts: CreditCard,

  // Insights
  reports: BarChart3,

  // Configuration Masters
  countries: Flag,
  'tax-rules': Percent,
  branches: Building2,
  locations: MapPin,
  lanes: GitFork,
  products: Box,
  'vehicle-types': Truck,
  'trailer-types': Container,
  'container-types': Container,
  'customer-groups': Users,
  milestones: Flag,
  charges: DollarSign,
  'document-types': FileText,
  technicians: Wrench,
  'workshop-bays': Sliders,
  'allowance-rules': Banknote,
}

export function getModuleIcon(key) {
  return MODULE_ICONS[key] || Layers
}
