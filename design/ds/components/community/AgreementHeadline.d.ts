/** "3 of 4 sources say covered" with the counts in 22px mono, and a caption saying whether the sources agree. */
export interface AgreementHeadlineProps {
  /** Number of publisher lines saying covered */
  covered: number;
  /** Number of publisher lines available */
  total: number;
  subject?: string;
}
export function AgreementHeadline(props: AgreementHeadlineProps): JSX.Element;
