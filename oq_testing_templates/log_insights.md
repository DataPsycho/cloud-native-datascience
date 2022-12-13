# Log Insights Query

```
fields @timestamp, @message
| filter @message like "INFO"
| parse @message "* [*] * - {'execution_time': *}" as @dt, @level, @thred, @execution_time
| filter @thred = "__main__"
| stats avg(@execution_time) as exec_time
by bin(10m)
| sort @timestamp desc
| limit 20
```