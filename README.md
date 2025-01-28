# disk_usage_exporter
Exporter for disk usage metrics.

## Installation
### From PyPi (soon)
```bash
sudo -H pip install disk_usage_exporter
```
### From source
1. Install `build` package
```bash
python -m pip install build
```
2. Build package
```bash
python -m build
```
3. Install package
```bash
VERSION=0.0.1
sudo -H pip install dist/disk_usage_exporter-$VERSION-py3-none-any.whl
```

## Prometheus configuration
`/etc/prometheus/prometheus.yml`
```yml
...
scrape_configs:
  - job_name: "disk_usage_exporter"
    static_configs:
      - targets: ["localhost:8100"] 
```

## Systemd unit
`/etc/systemd/system/disk_usage_exporter.service`
```ini
[Unit]
Description=disk_usage_exporter service

[Service]
ExecStart=disk_usage_exporter

[Install]
WantedBy=multi-user.target
```

## ToDo:
- [ ] Make getting values asynchronous
- [x] Make project structure similar to other prometheus exporters
- [ ] Add informative logging messages
- [x] Add CI with linter
- [x] Add tests
- [ ] Add name for python process
