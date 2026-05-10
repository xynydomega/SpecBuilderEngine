import React from 'react';
import { format } from 'date-fns';

interface TaskTimelineProps {
  timelineTitle: string;
}

export const TaskTimeline: React.FC<TaskTimelineProps> = ({ timelineTitle }) => {
  return (
    <div className="task-timeline">
      <h2>{timelineTitle}</h2>
      <p>Today: {format(new Date(), 'yyyy-MM-dd')}</p>
      <div className="timeline-grid">
        {/* Timeline items would go here */}
      </div>
    </div>
  );
};
