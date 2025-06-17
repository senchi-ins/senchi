export type CoverageItemProps = {
  title: string;
  description?: string;
  icon?: string;
};

export enum AvailableInsuranceTypes {
  HOME = "home",
  AUTO = "auto",
  RENTAL = "rental",
}

// The included object is a mapping from insurance type to a mapping of coverage keys to CoverageItemProps
export type IncludedType = {
  [key in AvailableInsuranceTypes]: {
    [coverageKey: string]: CoverageItemProps;
  };
};

export type InsuranceCoverageProps = {
  type: AvailableInsuranceTypes;
  coverages: CoverageItemProps[];
}