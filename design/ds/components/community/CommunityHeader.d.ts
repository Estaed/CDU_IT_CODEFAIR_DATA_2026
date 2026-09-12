/** Community name, region and type, population in mono, and the population's source line. Children (chips for what exists here) render beneath. */
export interface CommunityHeaderProps {
  name: string;
  region?: string;
  /** BushTel type, e.g. "Major community" */
  type?: string;
  population?: number;
  populationSource?: string;
  /** ISO date of the profile snapshot */
  populationDate?: string;
  children?: React.ReactNode;
}
export function CommunityHeader(props: CommunityHeaderProps): JSX.Element;
