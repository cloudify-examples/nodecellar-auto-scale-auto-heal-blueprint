(expired #(info "EXPIRED " %))

(where (service #"{{service_selector}}")
  #(info "got event: " %)
  (let [ hosts (atom #{}) ]
    (fn [e]
      ; store or remove host from set depending on whether it has expired.
      (let [ key (str (:host e) "." (:service e))]
        (do
          (if (expired? e)
            (swap! hosts disj key)
            (swap! hosts conj key)
          )
          ;save the host count
          (info "host cnt: " (count @hosts))
          (riemann.index/update index (assoc e :host nil :metric (max 1 (count @hosts)) :service "hostcount" ))
        )
      )
    )
  )

  (where (not (nil? (riemann.index/lookup index nil "hostcount")))
    (where (not (expired? event))
      (moving-time-window {{moving_window_size}}
        (smap folds/mean
          (fn [ev]
            (let [hostcnt (:metric (riemann.index/lookup index nil "hostcount"))
                  conns (/ (:metric ev) (max hostcnt 1))
                  cooling (not (nil? (riemann.index/lookup index "scaling" "suspended")))
                 ]
              (do
              (info "conns: " conns " cooling: " cooling)
              (if (and (not cooling) ({{scale_direction}} hostcnt {{scale_limit}}) ({{scale_direction}} {{scale_threshold}} conns))
                (do
                  (info "=== SCALE ===")
                  (process-policy-triggers ev)
                  (riemann.index/update index {:host "scaling" :service "suspended" :time (unix-time) :description "cooldown flag" :metric 0 :ttl {{cooldown_time}} :state "ok"})
                )
              )
              )
            )
          )
        )
      )
    )
  )
)
