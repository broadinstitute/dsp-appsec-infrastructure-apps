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
    threat_model: boolean;
    trivy: boolean;
    zap: boolean;
  }
