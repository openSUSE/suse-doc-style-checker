<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:py="https://www.gitorious.org/style-checker/style-checker"
  exclude-result-prefixes="py">
  <xsl:output method="xml" indent="yes" omit-xml-declaration="yes"/>

  <xsl:template match="*">
    <xsl:apply-templates/>
  </xsl:template>

  <xsl:template match="text()"/>

  <xsl:template match="/">
    <part>
      <part-title><xsl:apply-templates mode="part-title"/></part-title>
      <xsl:apply-templates/>
    </part>
  </xsl:template>

  <xsl:template name="sourcehint">
    <xsl:param name="node" select="."/>
    <place>
      <xsl:call-template name="file"/>
      <xsl:call-template name="withinid"/>
      <line><xsl:value-of select="py:linenumber()"/></line>
    </place>
  </xsl:template>

  <xsl:template name="file">
    <xsl:param name="node" select="."/>
    <xsl:if test="$node/ancestor::*[@xml:base]">
      <file>
        <xsl:value-of select="$node/ancestor::*[@xml:base][1]/@xml:base"/>
      </file>
    </xsl:if>
  </xsl:template>

  <xsl:template name="withinid">
    <xsl:param name="node" select="."/>
    <xsl:if test="$node/ancestor::*[@id]">
      <withinid>
        <xsl:value-of select="$node/ancestor::*[@id][1]/@id"/>
      </withinid>
    </xsl:if>
  </xsl:template>

  <xsl:template name="file-nomarkup">
    <xsl:param name="node" select="."/>
    <xsl:if test="$node/ancestor::*[@xml:base]">
        <xsl:value-of select="$node/ancestor::*[@xml:base][1]/@xml:base"/>
    </xsl:if>
  </xsl:template>

  <xsl:template name="withinid-nomarkup">
    <xsl:param name="node" select="."/>
    <xsl:if test="$node/ancestor::*[@id]">
        <xsl:value-of select="$node/ancestor::*[@id][1]/@id"/>
    </xsl:if>
  </xsl:template>

  <xsl:template name="createid">
    <xsl:param name="use-url-attribute" select="0"/>
    <xsl:param name="use-function-attribute" select="0"/>
    <xsl:param name="use-fileref-attribute" select="0"/>
    <xsl:param name="node" select="."/>

    <xsl:choose>
      <xsl:when test="$node/@id">
        <id><xsl:value-of select="$node/@id"/></id>
      </xsl:when>
      <xsl:otherwise>
        <xsl:choose>
          <xsl:when test="$node/title">
            <name><xsl:value-of select="normalize-space($node/title)"/></name>
          </xsl:when>
          <xsl:when test="$use-url-attribute = 1">
            <xsl:variable name="shortened">
              <xsl:choose>
                <xsl:when test="string-length(normalize-space($node/@url)) &gt; 53">
                  <xsl:value-of select="substring(normalize-space($node/@url), 1, 50)"/>…
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="normalize-space($node/@url)"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <name><xsl:value-of select="$shortened"/></name>
          </xsl:when>
          <xsl:when test="$use-function-attribute = 1">
            <xsl:variable name="shortened">
              <xsl:choose>
                <xsl:when test="string-length(normalize-space($node/@function)) &gt; 53">
                  <xsl:value-of select="substring(normalize-space($node/@function), 1, 50)"/>…
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="normalize-space($node/@function)"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <name><xsl:value-of select="$shortened"/></name>
          </xsl:when>
          <xsl:when test="$use-fileref-attribute = 1">
            <xsl:variable name="shortened">
              <xsl:choose>
                <xsl:when test="string-length(normalize-space($node/@fileref)) &gt; 53">
                  <xsl:value-of select="substring(normalize-space($node/@fileref), 1, 50)"/>…
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="normalize-space($node/@fileref)"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <name><xsl:value-of select="$shortened"/></name>
          </xsl:when>
          <xsl:otherwise>
            <xsl:variable name="shortened">
              <xsl:choose>
                <xsl:when test="string-length(normalize-space($node)) &gt; 53">
                  <xsl:value-of select="substring(normalize-space($node), 1, 50)"/>…
                </xsl:when>
                <xsl:otherwise>
                  <xsl:value-of select="normalize-space($node)"/>
                </xsl:otherwise>
              </xsl:choose>
            </xsl:variable>
            <name><xsl:value-of select="$shortened"/></name>
          </xsl:otherwise>
        </xsl:choose>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template name="safecharacters">
    <!-- The (unfulfilled) aim being to only allow [a-z][0-9]\.-_+ -->
    <xsl:param name="input" select="no_input"/>

    <xsl:value-of select="translate($input,
      'ABCDEFGHIJKLMNOPQRSTUVWXYZ?:;,!@#$%^§&amp;&lt;&gt;äàâãáåæÄÀÂÃÁÆÅçÇðÐèêéëËÉÈÊìîïíÍÏÌÎñÑòôõóöøœŒØÖÓÒÔÕùûüúÚÜÙÛýÿÝß©¢®þÞµ°[]“”{}|()= ',
      '')"/>
  </xsl:template>

  <xsl:template name="safecharacters-AZ">
    <!-- The (unfulfilled) aim being to only allow [a-z][0-9]\.-_+ -->
    <xsl:param name="input" select="no_input"/>

    <xsl:value-of select="translate($input, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', '')"/>
  </xsl:template>

  <xsl:template name="safecharacters-special">
    <!-- The (unfulfilled) aim being to only allow [a-z][0-9]\.-_+ -->
    <xsl:param name="input" select="no_input"/>

    <xsl:value-of select="translate($input,
      '?:;,!@#$%^§&amp;&lt;&gt;äàâãáåæÄÀÂÃÁÆÅçÇðÐèêéëËÉÈÊìîïíÍÏÌÎñÑòôõóöøœŒØÖÓÒÔÕùûüúÚÜÙÛýÿÝß©¢®þÞµ°[]“”{}|()= ',
      '')"/>
  </xsl:template>


  <!-- Template that starts terminology check. -->
  <xsl:template match="para|title|entry" mode="terminology">
    <xsl:if test="self::entry/para">
      <xsl:apply-templates mode="terminology"/>
    </xsl:if>
    <xsl:if test="not(ancestor-or-self::*/@role = 'legal')">
      <xsl:variable name="node" select="."/>
      <xsl:variable name="withinid">
        <xsl:call-template name="withinid-nomarkup"/>
      </xsl:variable>
      <xsl:variable name="file">
        <xsl:call-template name="file-nomarkup"/>
      </xsl:variable>
      <xsl:variable name="content-candidate">
        <xsl:apply-templates mode="terminology-content"/>
      </xsl:variable>
      <xsl:variable name="content-pretty-candidate">
        <xsl:apply-templates mode="content-pretty"/>
      </xsl:variable>
      <xsl:variable name="content"><xsl:value-of
        select="normalize-space($content-candidate)"/></xsl:variable>
      <xsl:variable name="content-pretty"><xsl:value-of
        select="normalize-space($content-pretty-candidate)"/></xsl:variable>

      <xsl:copy-of
        select="py:termcheck($termdataid, $content, $content-pretty, $withinid,
                             $file)"/>
    </xsl:if>
  </xsl:template>

  <xsl:template match="*" mode="terminology">
    <xsl:apply-templates mode="terminology"/>
  </xsl:template>

  <xsl:template match="text()" mode="terminology"/>


  <!-- Replace some elements for terminology checking itself. -->
  <xsl:template match="text()" mode="terminology-content">
    <xsl:value-of select="."/>
  </xsl:template>

  <xsl:template match="classname|code|command|computeroutput|constant|envar|
                       exceptionname|filename|function|interfacename|literal|
                       methodname|option|package|parameter|prompt|replaceable|
                       sgmltag|structfield|systemitem|tag|userinput|varname"
    mode="terminology-content">
    ##@mono##
  </xsl:template>

  <xsl:template match="keycombo|keycap" mode="terminology-content">
    ##@key##
  </xsl:template>

  <xsl:template match="menuchoice|guimenu" mode="terminology-content">
    ##@ui##
  </xsl:template>

  <xsl:template match="email|filename|ulink|uri|xref" mode="terminology-content">
    ##@ref##
  </xsl:template>

  <xsl:template match="remark|indexterm" mode="terminology-content"/>

  <xsl:template match="*" mode="terminology-content">
    <xsl:apply-templates mode="terminology-content"/>
  </xsl:template>


  <!-- Semi-format some elements for terminology check output. -->
  <xsl:template match="*" mode="content-pretty">
    <xsl:apply-templates mode="content-pretty"/>
  </xsl:template>

  <xsl:template match="text()" mode="content-pretty">
    <xsl:value-of select="."/>
  </xsl:template>

  <xsl:template match="keycap" mode="content-pretty">
    <xsl:choose>
      <xsl:when test="@function">
        <xsl:choose>
          <xsl:when test="@function = 'alt'">Alt</xsl:when>
          <xsl:when test="@function = 'backspace'">&lt;&#x2014;</xsl:when>
          <xsl:when test="@function = 'command'">&#x2318;</xsl:when>
          <xsl:when test="@function = 'control'">Ctrl</xsl:when>
          <xsl:when test="@function = 'delete'">Del</xsl:when>
          <xsl:when test="@function = 'down'">&#x02193;</xsl:when>
          <xsl:when test="@function = 'end'">End</xsl:when>
          <xsl:when test="@function = 'enter'">Enter</xsl:when>
          <xsl:when test="@function = 'escape'">Esc</xsl:when>
          <xsl:when test="@function = 'home'">Home</xsl:when>
          <xsl:when test="@function = 'insert'">Ins</xsl:when>
          <xsl:when test="@function = 'left'">&#x02190;</xsl:when>
          <xsl:when test="@function = 'meta'">Meta</xsl:when>
          <xsl:when test="@function = 'pagedown'">Page &#x02193;</xsl:when>
          <xsl:when test="@function = 'pageup'">Page &#x02191;</xsl:when>
          <xsl:when test="@function = 'right'">&#x02192;</xsl:when>
          <xsl:when test="@function = 'shift'">Shift</xsl:when>
          <xsl:when test="@function = 'space'">Space</xsl:when>
          <xsl:when test="@function = 'tab'">&#x02192;|</xsl:when>
          <xsl:when test="@function = 'up'">&#x02191;</xsl:when>
          <xsl:otherwise>???</xsl:otherwise>
        </xsl:choose>
      </xsl:when>
      <xsl:otherwise>
        <xsl:apply-templates mode="content-pretty"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="keycombo" mode="content-pretty">
    <xsl:for-each select="*">
      <xsl:if test="position()&gt;1">–</xsl:if>
      <xsl:apply-templates mode="content-pretty" select="."/>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="menuchoice" mode="content-pretty">
    <xsl:for-each select="*">
      <xsl:if test="position()&gt;1"> &gt; </xsl:if>
      <xsl:apply-templates mode="content-pretty" select="."/>
    </xsl:for-each>
  </xsl:template>

  <xsl:template match="xref" mode="content-pretty">
      <xsl:value-of select="@linkend"/>
  </xsl:template>

  <xsl:template match="ulink" mode="content-pretty">
    <xsl:choose>
      <xsl:when test="text()">
        <xsl:value-of select="."/>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="@url"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

  <xsl:template match="remark|indexterm" mode="content-pretty"/>

</xsl:stylesheet>
