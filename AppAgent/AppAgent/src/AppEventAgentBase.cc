#include "AppEventAgentBase.h"
#include <DMI/Record.h>

namespace AppAgent
{    

static int dum = aidRegistry_AppAgent();

//##ModelId=3E414887001F
AppEventAgentBase::AppEventAgentBase (const HIID &initf)
    : AppAgent(initf)
{
  sink_ <<= new AppEventSink(HIID());
}

//##ModelId=3E47AA530111
void AppEventAgentBase::attach(AppEventFlag& evflag, int dmiflags)
{
  sink().attach(evflag,dmiflags);
}

//##ModelId=3E4148870295
AppEventAgentBase::AppEventAgentBase (AppEventSink &evsink,const HIID &initf,int flags)
    : AppAgent(initf)
{
  sink_.attach(evsink,flags); 
}

//##ModelId=3E50F9BB019B
AppEventAgentBase::AppEventAgentBase (AppEventSink *evsink,const HIID &initf,int flags)
    : AppAgent(initf)
{
  sink_.attach(evsink,flags);
}

//##ModelId=3E47AF920205
bool AppEventAgentBase::isAsynchronous() const
{
  return sink().isAsynchronous();
}

//##ModelId=3E41147B0049
bool AppEventAgentBase::init (const DMI::Record &data)
{
  const DMI::Record dum;
  return sink().init(data[initfield()].as<DMI::Record>(dum));
}

//##ModelId=3E41147E0126
void AppEventAgentBase::close ()
{
  sink().close();
}

//##ModelId=3E41141201DE
int AppEventAgentBase::state () const
{
  return sink().state();
}

//##ModelId=3E411412024B
string AppEventAgentBase::stateString () const
{
  return sink().stateString();
}

//##ModelId=3E4148900162
string AppEventAgentBase::sdebug (int detail, const string &prefix, const char *name) const
{
  using Debug::append;
  using Debug::appendf;
  using Debug::ssprintf;
  
  string out;
  if( detail >= 0 ) // basic detail
  {
    appendf(out,"%s/%08x",name?name:"AppEventAgentBase",(int)this);
  }
  if( detail >= 1 || detail == -1 )
  {
    appendf(out,"st:%d",state());
  }
  if( detail >= 2 || detail == -2 )
  {
    append(out,stateString());
  }
  if( detail >= 3 || detail == -3 )
  {
    out += "\n" + prefix + "  sink: " + sink().sdebug(abs(detail)-1,prefix+"  ");
  }
  
  return out;
}
//##ModelId=3E4295C503C9
void AppEventAgentBase::fillReceiveEventList (DMI::Record &)
{
}

//##ModelId=3E42973F0398
void AppEventAgentBase::fillPostEventList (DMI::Record &)
{
}

//##ModelId=3E42967E027F
const DMI::Record & AppEventAgentBase::receiveEventList ()
{
  static DMI::Record dum;
  return dum;
}

//##ModelId=3E4296940160
const DMI::Record & AppEventAgentBase::postEventList ()
{
  static DMI::Record dum;
  return dum;
}

};
