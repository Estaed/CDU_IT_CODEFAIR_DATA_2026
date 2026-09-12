/** Grey block with a 3px ochre left rule, printed beneath any Degraded verdict to state the assumption it rests on. */
export interface AssumptionNoteProps {
  /** Text with figures in backticks; alternative to children */
  text?: string;
  children?: React.ReactNode;
  label?: string;
}
export function AssumptionNote(props: AssumptionNoteProps): JSX.Element;
