#[derive(Clone, Copy, PartialEq)]
pub enum RequestType {
    GET_RESULTS,
    STATES_MEAN,
    STATE_MEAN,
    BEST_5,
    WORST_5,
    GLOBAL_MEAN,
    DIFF_FROM_MEAN,
    STATE_DIFF_FROM_MEAN,
    MEAN_BY_CATEGORY,
    STATE_MEAN_BY_CATEGORY
}


impl RequestType {
    pub fn as_str(&self) -> &'static str {
        match self  {
            RequestType::GET_RESULTS => "/api/get_results/<job_id>",
            RequestType::STATES_MEAN => "/api/states_mean",
            RequestType::STATE_MEAN => "/api/state_mean",
            RequestType::BEST_5 => "/api/best5",
            RequestType::WORST_5 => "/api/worst5",
            RequestType::GLOBAL_MEAN => "/api/global_mean",
            RequestType::DIFF_FROM_MEAN => "/api/diff_from_mean",
            RequestType::STATE_DIFF_FROM_MEAN => "/api/state_diff_from_mean",
            RequestType::MEAN_BY_CATEGORY => "/api/mean_by_category",
            RequestType::STATE_MEAN_BY_CATEGORY => "/api/state_mean_by_category"
        }
    }
}