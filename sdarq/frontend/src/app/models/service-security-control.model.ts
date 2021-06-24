import {Deserializable} from './deserializable.model';

export class ServiceSecurityControl implements Deserializable {
    deserialize(input: any): this {
        Object.assign(this, input);
        return this;
    }
    service: string;
    product: string;
    burp: boolean;
    cis_scanner: boolean;
    dev_url: string;
    github: string;
    sourceclear: boolean;
    sourceclear_link: string;
    threat_model: boolean;
    docker_scan: boolean;
    zap: boolean;
    CodeDx: string;
    defect_dojo: string;
  }
