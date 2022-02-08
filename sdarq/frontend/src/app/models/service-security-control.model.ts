import {Deserializable} from './deserializable.model';

export class ServiceSecurityControl implements Deserializable {
    deserialize(input: any): this {
        Object.assign(this, input);
        return this;
    }
    service: string;
    product: string;
    security_champion: string;
    burp: boolean;
    security_pentest_link: string;
    cis_scanner: boolean;
    dev_url: string;
    github: string;
    sourceclear: boolean;
    sourceclear_link: string;
    threat_model: boolean;
    threat_model_link: string;
    docker_scan: boolean;
    zap: boolean;
    vulnerability_management: string;
    defect_dojo: string;
  }
