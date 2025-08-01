/**
 * Message Patterns for Question Type Detection
 * Regex patterns to identify different types of user questions
 */

export const QUESTION_PATTERNS = {
  'show-data': [
    /show.*data/i,
    /display.*information/i,
    /get.*details/i,
    /what.*status/i,
    /current.*metrics/i,
    /view.*data/i,
    /see.*information/i,
    /fetch.*data/i,
    /retrieve.*information/i,
    /give.*me.*data/i
  ],
  
  'create-chart': [
    /create.*chart/i,
    /show.*graph/i,
    /visualize/i,
    /plot.*data/i,
    /generate.*chart/i,
    /make.*graph/i,
    /draw.*chart/i,
    /build.*visualization/i,
    /chart.*for/i,
    /graph.*of/i
  ],
  
  'trend-analysis': [
    /trend/i,
    /over time/i,
    /monthly/i,
    /yearly/i,
    /compare.*period/i,
    /historical/i,
    /time.*series/i,
    /progression/i,
    /evolution/i,
    /pattern.*over/i
  ],
  
  'comparison': [
    /compare/i,
    /vs/i,
    /versus/i,
    /difference/i,
    /between.*and/i,
    /contrast/i,
    /against/i,
    /relative.*to/i,
    /compared.*with/i,
    /benchmark/i
  ],
  
  'summary': [
    /summary/i,
    /overview/i,
    /report/i,
    /status/i,
    /dashboard/i,
    /brief/i,
    /snapshot/i,
    /highlights/i,
    /key.*points/i,
    /executive.*summary/i
  ],
  
  'specific-metric': [
    /how many/i,
    /total/i,
    /count/i,
    /percentage/i,
    /rate/i,
    /average/i,
    /number.*of/i,
    /quantity/i,
    /amount/i,
    /frequency/i
  ],
  
  'analysis': [
    /analyze/i,
    /analysis/i,
    /insights/i,
    /patterns/i,
    /correlations/i,
    /relationships/i,
    /deep.*dive/i,
    /investigate/i,
    /examine/i,
    /study/i
  ],
  
  'prediction': [
    /predict/i,
    /forecast/i,
    /future/i,
    /projection/i,
    /estimate/i,
    /anticipate/i,
    /expect/i,
    /likely/i,
    /probable/i,
    /upcoming/i
  ],
  
  'alert': [
    /alert/i,
    /warning/i,
    /critical/i,
    /urgent/i,
    /immediate/i,
    /priority/i,
    /attention/i,
    /issue/i,
    /problem/i,
    /concern/i
  ],
  
  'compliance': [
    /compliance/i,
    /regulation/i,
    /standard/i,
    /requirement/i,
    /audit/i,
    /certification/i,
    /policy/i,
    /procedure/i,
    /guideline/i,
    /protocol/i
  ]
};

export const MODULE_KEYWORDS = {
  'incident-investigation': [
    /incident/i,
    /accident/i,
    /injury/i,
    /near.*miss/i,
    /investigation/i,
    /report/i,
    /occurrence/i,
    /event/i,
    /mishap/i,
    /casualty/i
  ],
  
  'risk-assessment': [
    /risk/i,
    /hazard/i,
    /assessment/i,
    /danger/i,
    /threat/i,
    /vulnerability/i,
    /exposure/i,
    /probability/i,
    /likelihood/i,
    /severity/i
  ],
  
  'action-tracking': [
    /action/i,
    /task/i,
    /tracking/i,
    /follow.*up/i,
    /completion/i,
    /progress/i,
    /assignment/i,
    /responsibility/i,
    /deadline/i,
    /overdue/i
  ],
  
  'driver-safety': [
    /driver/i,
    /vehicle/i,
    /checklist/i,
    /fitness/i,
    /license/i,
    /driving/i,
    /transport/i,
    /fleet/i,
    /automotive/i,
    /road.*safety/i
  ],
  
  'observation-tracker': [
    /observation/i,
    /inspection/i,
    /monitoring/i,
    /surveillance/i,
    /watch/i,
    /check/i,
    /review/i,
    /audit/i,
    /assessment/i,
    /evaluation/i
  ],
  
  'equipment-asset': [
    /equipment/i,
    /asset/i,
    /machinery/i,
    /tool/i,
    /device/i,
    /instrument/i,
    /calibration/i,
    /maintenance/i,
    /inspection/i,
    /repair/i
  ],
  
  'employee-training': [
    /training/i,
    /employee/i,
    /education/i,
    /certification/i,
    /course/i,
    /skill/i,
    /competency/i,
    /qualification/i,
    /development/i,
    /learning/i
  ]
};

export const COMPLEXITY_INDICATORS = {
  'simple': [
    /show/i,
    /display/i,
    /get/i,
    /view/i,
    /see/i
  ],
  
  'medium': [
    /analyze/i,
    /compare/i,
    /trend/i,
    /pattern/i,
    /summary/i
  ],
  
  'complex': [
    /comprehensive/i,
    /detailed/i,
    /deep.*dive/i,
    /correlation/i,
    /relationship/i,
    /cross.*module/i,
    /multi.*dimensional/i,
    /holistic/i,
    /integrated/i,
    /advanced/i
  ]
};

export const TIME_INDICATORS = {
  'recent': [
    /recent/i,
    /latest/i,
    /current/i,
    /today/i,
    /this.*week/i,
    /this.*month/i
  ],
  
  'historical': [
    /historical/i,
    /past/i,
    /previous/i,
    /last.*year/i,
    /archive/i,
    /old/i
  ],
  
  'custom': [
    /between/i,
    /from.*to/i,
    /specific.*date/i,
    /range/i,
    /period/i
  ]
};
