.PHONY: build prepare config run run-debug stop clean setup-env generate-config update-config clean-config build-network run-network run-network-debug stop-network clean-network run-monitoring stop-monitoring clean-monitoring

# Reset this variable to chose the topology which should be deployed
RESOURCE_FILE = ${CONFIG_GEN_DIR}/resources/large_network.yaml

P4_DIR = network/p4
P4_LOG_DIR = ${P4_DIR}/logs
P4_BUILD_DIR = ${P4_DIR}/build
P4_PCAP_DIR = ${P4_DIR}/pcaps
CONFIG_GEN_DIR = config/generator
CONFIG_GEN_OUT_DIR = ${CONFIG_GEN_DIR}/out
CONFIG_UPDATE_DIR = config/updater
CONFIG_UPDATE_CHKSUM_FILE = ${CONFIG_UPDATE_DIR}/checksums.json
CONFIG_LOG_DIR = config/logs

GRAFANA_ENV_DATASOURCE_DIR = monitoring/grafana/envsubst
GRAFANA_DATASOURCE_DIR = monitoring/grafana/provisioning/datasources
INFLUX_ENV_SCRIPT_DIR = monitoring/influx/envsubst
INFLUX_SCRIPT_DIR = monitoring/influx/entrypoint

P4C = p4c-bm2-ss
P4C_ARGS += --p4runtime-files $(P4_BUILD_DIR)/main.p4.p4info.txt --emit-externs

RUN_NETWORK_SCRIPT = network/utils/run_network.py

BMV2_SWITCH_EXE = simple_switch_grpc
BMV2_REPO = ${HOME}/git/ba/behavioral-model
BMV2_EXTERN_DIR = ${BMV2_REPO}/externs/obj
BMV2_EXTERNS = ${BMV2_EXTERN_DIR}/ipfix.so # comma separated list

# Define NO_P4 to start BMv2 without a program
ifndef NO_P4
run_args += -j $(P4_BUILD_DIR)/main.json
endif

# Set BMV2_SWITCH_EXE to override the BMv2 target
ifdef BMV2_SWITCH_EXE
run_args += -b $(BMV2_SWITCH_EXE)
endif

# Set BMV2_EXTERNS to define BMV2 modules (shared libraries)
ifdef BMV2_EXTERNS
run_args += -m $(BMV2_EXTERNS)
endif

# Include environment variables specific to monitoring
include monitoring/.env
export

build: build-network

prepare: setup-env

config: generate-config update-config

run: prepare build generate-config run-monitoring run-network

run-debug: prepare build generate-config run-monitoring run-network-debug

stop: stop-network stop-monitoring

clean: clean-network clean-monitoring clean-config

### prepare tasks ###

setup-env:
	mkdir -p ${GRAFANA_DATASOURCE_DIR}
	mkdir -p ${INFLUX_SCRIPT_DIR}
	envsubst < ${GRAFANA_ENV_DATASOURCE_DIR}/datasource.yaml > ${GRAFANA_DATASOURCE_DIR}/datasource.yaml
	envsubst < ${INFLUX_ENV_SCRIPT_DIR}/create_buckets.sh > ${INFLUX_SCRIPT_DIR}/create_buckets.sh && chmod +x ${INFLUX_SCRIPT_DIR}/create_buckets.sh

### config tasks ###

generate-config:
	uv run ${CONFIG_GEN_DIR}/main.py \
	--template-dir $(CONFIG_GEN_DIR)/templates \
	--grafana-template-dir $(CONFIG_GEN_DIR)/templates/grafana \
	--mininet-template mininet_topology.j2 \
	--bmv2-template bmv2_runtime.j2 \
	--grafana-dashboard-dir monitoring/grafana/dashboards \
	--resources $(RESOURCE_FILE) \
	--log-dir $(CONFIG_LOG_DIR) \
	--out-dir ${CONFIG_GEN_OUT_DIR}

update-config:
	uv run ${CONFIG_UPDATE_DIR}/updater.py

clean-config:
	rm -rf ${CONFIG_LOG_DIR} ${CONFIG_GEN_OUT_DIR} ${CONFIG_UPDATE_CHKSUM_FILE}


### network tasks ###

build-network:
	mkdir -p $(P4_BUILD_DIR)
	$(P4C) --p4v 16 $(P4C_ARGS) -o $(P4_BUILD_DIR)/main.json ${P4_DIR}/main.p4

run-network: build generate-config
	mkdir -p $(P4_LOG_DIR)
	sudo python3 $(RUN_NETWORK_SCRIPT) -t $(CONFIG_GEN_OUT_DIR)/topology.json $(run_args) -l $(P4_LOG_DIR)

run-network-debug: build generate-config
	mkdir -p $(P4_PCAP_DIR) $(P4_LOG_DIR)
	sudo python3 $(RUN_NETWORK_SCRIPT) -t $(CONFIG_GEN_OUT_DIR)/topology.json $(run_args) -l $(P4_LOG_DIR) -p $(P4_PCAP_DIR) --bmv2-log-console

stop-network:
	sudo mn -c

clean-network: stop-network
	rm -rf ${P4_LOG_DIR} ${P4_BUILD_DIR} ${P4_PCAP_DIR}


### monitor tasks ###

run-monitoring: build generate-config
	sudo docker compose -f monitoring/docker-compose.yaml up --detach

stop-monitoring:
	sudo docker compose -f monitoring/docker-compose.yaml down

clean-monitoring: stop-monitoring
	rm -rf ${GRAFANA_DATASOURCE_DIR} ${INFLUX_SCRIPT_DIR}
	sudo docker volume prune -a
