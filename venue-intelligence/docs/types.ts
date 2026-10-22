/** UI/agent-facing proposal only; not a live API. */
export type EvidencePolicy = 'yes'|'no'|'restricted'|'unknown';
export type ReviewStatus = 'page_reviewed'|'url_discovered'|'previous_research';
export interface VenueLead {
  venue_id: string;
  legacy_venue_id?: string;
  display_name: string;
  building_id: string;
  building_name: string;
  space_id: string;
  room_name: string | null;
  operator_id: string | null;
  venue_type: string;
  source_url: string;
  source_class: string;
  review_status: ReviewStatus;
  source_domain: string;
  borough: string | null;
  postcode: string | null;
  street_address: string | null;
  latitude: number | null;
  longitude: number | null;
  capacity_laptops: number | null;
  capacity_classroom: number | null;
  capacity_theatre: number | null;
  capacity_standing: number | null;
  capacity_boardroom: number | null;
  capacity_cabaret: number | null;
  area_sqm: number | null;
  fibre_mbps: number | null;
  price_gbp_from: number | null;
  price_unit: string | null;
  price_conditions: string | null;
  after18_policy: EvidencePolicy;
  weekend_policy: EvidencePolicy;
  overnight_policy: EvidencePolicy;
  wifi_status: EvidencePolicy;
  av_status: EvidencePolicy;
  power_status: EvidencePolicy;
  accessibility_status: EvidencePolicy;
  catering_status: EvidencePolicy;
  breakout_status: EvidencePolicy;
  hours_weekday_evening_text?: string | null;
  hours_weekend_text?: string | null;
  booking_url: string | null;
  research_priority: number;
  quality_fields_present: number;
  acquisition_batch: 'legacy'|'v2';
  listing_granularity: 'space'|'building_or_unspecified';
  availability_live: false;
  can_advertise_available: false;
  is_currently_bookable: false;
  lead_status: 'research_lead';
}
export interface VenueEvidence {
  evidence_id: string;
  venue_id: string;
  field: string;
  value: string|number|boolean;
  source_url: string;
  source_class: string;
  observed_date: string|null;
  caveat: string|null;
  evidence_text: string|null;
}
export interface KnowledgeEdge {
  from_id: string;
  predicate: 'OPERATES'|'HAS_SPACE'|'DESCRIBED_BY';
  to_id: string;
  source_url: string;
}
