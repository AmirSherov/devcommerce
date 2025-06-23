declare module '@tabler/icons-react' {
  import { FC, SVGProps } from 'react';
  
  export interface TablerIconProps extends SVGProps<SVGSVGElement> {
    size?: number | string;
    stroke?: number;
    color?: string;
  }
  
  export const IconBrandGithub: FC<TablerIconProps>;
  export const IconBrandGoogle: FC<TablerIconProps>;
} 