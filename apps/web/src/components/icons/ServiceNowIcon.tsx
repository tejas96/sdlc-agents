import React from 'react';
import { IconProps } from './types';

export const ServiceNowIcon: React.FC<IconProps> = ({
  className = 'h-8 w-8',
}) => {
  return (
    <svg
      className={className}
      viewBox='0 0 71.1 63.6'
      fill='none'
      xmlns='http://www.w3.org/2000/svg'
    >
      <path
        fillRule='evenodd'
        clipRule='evenodd'
        d='M35.8,0C16.1,0,0,15.9,0,35.6c0,9.8,4,19.3,11.2,26c2.5,2.4,6.4,2.6,9.2,0.5c9-6.7,21.4-6.7,30.4,0
		c2.8,2.1,6.7,1.9,9.2-0.5C74.3,48,74.9,25.4,61.3,11.1C54.7,4.1,45.4,0.1,35.8,0 M35.6,53.5C26,53.8,18,46.2,17.8,36.7
		c0-0.3,0-0.6,0-0.9c0-9.8,8-17.8,17.8-17.8s17.8,8,17.8,17.8c0.3,9.6-7.3,17.5-16.8,17.8C36.2,53.5,35.9,53.5,35.6,53.5'
        fill='#62D84E'
      />
    </svg>
  );
};
