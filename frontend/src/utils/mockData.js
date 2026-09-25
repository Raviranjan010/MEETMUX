/**
 * Fallback Operational Snapshot Data for RunwayOptx
 * Used seamlessly when backend API is starting up, cold-booting, or offline in deployment links
 */

export const DEFAULT_DASHBOARD_DATA = {
  kpis: {
    total_flights: 48,
    delayed_flights: 12,
    delayed_percentage: 25.0,
    average_predicted_delay_minutes: 10.8,
    gates_available: 8,
    gates_utilized: 16,
    gates_total: 24,
    gate_utilization_rate: 66.7,
    active_conflicts: 0,
    latest_optimization_status: "OPTIMAL",
    latest_optimization_objective: 142.5,
    latest_solver_runtime_seconds: 0.082
  },
  delay_distribution: [
    { category: 'On Time', count: 36, percentage: 75.0, color: '#19D88A' },
    { category: 'Low', count: 6, percentage: 12.5, color: '#FFC857' },
    { category: 'Moderate', count: 4, percentage: 8.3, color: '#FF9F1C' },
    { category: 'High', count: 2, percentage: 4.2, color: '#FF4D4D' },
    { category: 'Severe', count: 0, percentage: 0.0, color: '#FF3333' }
  ],
  delay_by_airline: [
    { airline: 'Air India', avg_delay: 14.2, flight_count: 16, delayed_count: 5 },
    { airline: 'IndiGo', avg_delay: 7.8, flight_count: 20, delayed_count: 3 },
    { airline: 'SpiceJet', avg_delay: 16.5, flight_count: 6, delayed_count: 3 },
    { airline: 'Vistara', avg_delay: 6.1, flight_count: 6, delayed_count: 1 }
  ],
  congestion_by_hour: Array.from({ length: 24 }, (_, h) => {
    const isPeak = (h >= 8 && h <= 11) || (h >= 17 && h <= 21);
    const arr = isPeak ? Math.floor(Math.random() * 5) + 12 : Math.floor(Math.random() * 4) + 3;
    const dep = isPeak ? Math.floor(Math.random() * 5) + 11 : Math.floor(Math.random() * 4) + 2;
    return {
      hour: h,
      time_label: `${String(h).padStart(2, '0')}:00`,
      arrivals: arr,
      departures: dep,
      total_flights: arr + dep,
      avg_delay: isPeak ? 16.4 : 5.2
    };
  }),
  gate_occupancy: [
    { gate_id: 1, gate_number: 'G11', terminal: 'T1', flight_id: 101, flight_number: 'AI501', airline: 'Air India', aircraft_type: 'A320', start_time: new Date(Date.now() - 20 * 60000).toISOString(), end_time: new Date(Date.now() + 40 * 60000).toISOString(), delay_minutes: 3.5, delay_category: 'On Time', status: 'OPTIMAL' },
    { gate_id: 2, gate_number: 'G12', terminal: 'T1', flight_id: 102, flight_number: '6E204', airline: 'IndiGo', aircraft_type: 'A321', start_time: new Date(Date.now() - 10 * 60000).toISOString(), end_time: new Date(Date.now() + 50 * 60000).toISOString(), delay_minutes: 18.0, delay_category: 'Moderate', status: 'OPTIMAL' },
    { gate_id: 3, gate_number: 'G14', terminal: 'T1', flight_id: 103, flight_number: 'SG612', airline: 'SpiceJet', aircraft_type: 'B737', start_time: new Date(Date.now() + 15 * 60000).toISOString(), end_time: new Date(Date.now() + 75 * 60000).toISOString(), delay_minutes: 8.0, delay_category: 'Low', status: 'OPTIMAL' },
    { gate_id: 4, gate_number: 'G15', terminal: 'T2', flight_id: 104, flight_number: 'UK953', airline: 'Vistara', aircraft_type: 'A320', start_time: new Date(Date.now() - 30 * 60000).toISOString(), end_time: new Date(Date.now() + 30 * 60000).toISOString(), delay_minutes: 2.0, delay_category: 'On Time', status: 'OPTIMAL' },
    { gate_id: 5, gate_number: 'G16', terminal: 'T2', flight_id: 105, flight_number: 'AI782', airline: 'Air India', aircraft_type: 'B787', start_time: new Date(Date.now() + 5 * 60000).toISOString(), end_time: new Date(Date.now() + 65 * 60000).toISOString(), delay_minutes: 32.0, delay_category: 'High', status: 'OPTIMAL' },
    { gate_id: 6, gate_number: 'G18', terminal: 'T3', flight_id: 106, flight_number: '6E911', airline: 'IndiGo', aircraft_type: 'A320', start_time: new Date(Date.now() - 5 * 60000).toISOString(), end_time: new Date(Date.now() + 55 * 60000).toISOString(), delay_minutes: 4.2, delay_category: 'On Time', status: 'OPTIMAL' },
    { gate_id: 7, gate_number: 'G21', terminal: 'T3', flight_id: 107, flight_number: 'AI102', airline: 'Air India', aircraft_type: 'B777', start_time: new Date(Date.now() + 25 * 60000).toISOString(), end_time: new Date(Date.now() + 85 * 60000).toISOString(), delay_minutes: 12.5, delay_category: 'Low', status: 'OPTIMAL' },
    { gate_id: 8, gate_number: 'G22', terminal: 'T3', flight_id: 108, flight_number: 'UK814', airline: 'Vistara', aircraft_type: 'A321', start_time: new Date(Date.now() - 40 * 60000).toISOString(), end_time: new Date(Date.now() + 20 * 60000).toISOString(), delay_minutes: 1.5, delay_category: 'On Time', status: 'OPTIMAL' }
  ],
  weather_impact: [
    { condition: 'Clear', avg_delay: 4.2, count: 22 },
    { condition: 'Overcast', avg_delay: 7.9, count: 12 },
    { condition: 'Rain', avg_delay: 14.8, count: 8 },
    { condition: 'Fog', avg_delay: 26.5, count: 5 },
    { condition: 'Thunderstorm', avg_delay: 38.2, count: 3 }
  ],
  predicted_vs_actual: [
    { flight_number: 'AI501', predicted: 4.2, actual: 3.5 },
    { flight_number: '6E204', predicted: 16.5, actual: 18.0 },
    { flight_number: 'SG612', predicted: 9.0, actual: 8.0 },
    { flight_number: 'UK953', predicted: 3.1, actual: 2.0 },
    { flight_number: 'AI782', predicted: 28.4, actual: 32.0 },
    { flight_number: '6E911', predicted: 5.0, actual: 4.2 },
    { flight_number: 'AI102', predicted: 11.8, actual: 12.5 },
    { flight_number: 'UK814', predicted: 2.5, actual: 1.5 },
    { flight_number: '6E452', predicted: 7.8, actual: 8.2 },
    { flight_number: 'SG301', predicted: 21.0, actual: 19.5 }
  ]
};

export const DEFAULT_FLIGHTS = [
  { id: 1, flight_number: 'AI501', airline: 'Air India', aircraft_type: 'A320', origin: 'BOM', destination: 'DEL', scheduled_arrival: new Date().toISOString(), scheduled_departure: new Date(Date.now() + 60*60000).toISOString(), terminal: 'T3', assigned_gate: 'G11', taxi_in_minutes: 4.0, latest_predicted_delay: 3.5, latest_delay_category: 'On Time', status: 'Scheduled' },
  { id: 2, flight_number: '6E204', airline: 'IndiGo', aircraft_type: 'A321', origin: 'BLR', destination: 'DEL', scheduled_arrival: new Date(Date.now() + 15*60000).toISOString(), scheduled_departure: new Date(Date.now() + 75*60000).toISOString(), terminal: 'T1', assigned_gate: 'G12', taxi_in_minutes: 16.0, latest_predicted_delay: 18.0, latest_delay_category: 'Moderate', status: 'Delayed' },
  { id: 3, flight_number: 'SG612', airline: 'SpiceJet', aircraft_type: 'B737', origin: 'MAA', destination: 'DEL', scheduled_arrival: new Date(Date.now() + 30*60000).toISOString(), scheduled_departure: new Date(Date.now() + 90*60000).toISOString(), terminal: 'T1', assigned_gate: 'G14', taxi_in_minutes: 8.0, latest_predicted_delay: 8.0, latest_delay_category: 'Low', status: 'Boarding' },
  { id: 4, flight_number: 'UK953', airline: 'Vistara', aircraft_type: 'A320', origin: 'HYD', destination: 'DEL', scheduled_arrival: new Date(Date.now() + 45*60000).toISOString(), scheduled_departure: new Date(Date.now() + 105*60000).toISOString(), terminal: 'T3', assigned_gate: 'G15', taxi_in_minutes: 3.0, latest_predicted_delay: 2.0, latest_delay_category: 'On Time', status: 'Scheduled' },
  { id: 5, flight_number: 'AI782', airline: 'Air India', aircraft_type: 'B787', origin: 'DXB', destination: 'DEL', scheduled_arrival: new Date(Date.now() + 60*60000).toISOString(), scheduled_departure: new Date(Date.now() + 120*60000).toISOString(), terminal: 'T3', assigned_gate: 'G16', taxi_in_minutes: 25.0, latest_predicted_delay: 32.0, latest_delay_category: 'High', status: 'Delayed' },
  { id: 6, flight_number: '6E911', airline: 'IndiGo', aircraft_type: 'A320', origin: 'CCU', destination: 'DEL', scheduled_arrival: new Date(Date.now() + 75*60000).toISOString(), scheduled_departure: new Date(Date.now() + 135*60000).toISOString(), terminal: 'T2', assigned_gate: 'G18', taxi_in_minutes: 5.0, latest_predicted_delay: 4.2, latest_delay_category: 'On Time', status: 'Scheduled' },
  { id: 7, flight_number: 'AI102', airline: 'Air India', aircraft_type: 'B777', origin: 'JFK', destination: 'DEL', scheduled_arrival: new Date(Date.now() + 90*60000).toISOString(), scheduled_departure: new Date(Date.now() + 150*60000).toISOString(), terminal: 'T3', assigned_gate: 'G21', taxi_in_minutes: 12.0, latest_predicted_delay: 12.5, latest_delay_category: 'Low', status: 'Scheduled' },
  { id: 8, flight_number: 'UK814', airline: 'Vistara', aircraft_type: 'A321', origin: 'PNQ', destination: 'DEL', scheduled_arrival: new Date(Date.now() + 105*60000).toISOString(), scheduled_departure: new Date(Date.now() + 165*60000).toISOString(), terminal: 'T3', assigned_gate: 'G22', taxi_in_minutes: 2.0, latest_predicted_delay: 1.5, latest_delay_category: 'On Time', status: 'Scheduled' }
];
