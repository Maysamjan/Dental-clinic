export interface User {
  id: number;
  username: string;
  full_name: string;
  email: string;
  role: number | null;
  role_code: string | null;
  role_name: string | null;
  permissions: string[];
}

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Patient {
  id: number;
  code: string;
  full_name: string;
  gender: string;
  age: number | null;
  date_of_birth: string | null;
  phone: string;
  address: string;
  medical_history: string;
  allergies: string;
  is_archived: boolean;
}

export interface QueueItem {
  id: number;
  queue_number: number;
  patient: number;
  patient_name: string;
  arrival_time: string;
  workflow_status: string;
  medical_summary: string;
}

export interface DashboardSummary {
  total_patients: number;
  todays_patients: number;
  todays_appointments: number;
  todays_revenue: string;
  outstanding_invoices: number;
  outstanding_balance: string;
  upcoming_followups: number;
  inventory_alerts: number;
  queue_size: number;
  recent_activities: { action: string; entity: string; summary: string; created_at: string }[];
}
