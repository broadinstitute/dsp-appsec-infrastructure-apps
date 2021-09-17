// This interface will deserialize JSON received from GET endpoints to objects
export interface Deserializable {
    deserialize(input: any): this;
  }
